from __future__ import division, print_function

import time

from math import modf,sqrt
from serial import Serial
from serial.tools.list_ports import comports

from .paths import path_length
from .planner import Planner
from .progress import Bar


BAUDRATE = 115200

TIMESLICE_MS = 10

MICROSTEPPING_MODE = 1
STEP_DIVIDER = 2 ** (MICROSTEPPING_MODE - 1)

STEPS_PER_INCH = 2032 / STEP_DIVIDER
STEPS_PER_MM = 80 / STEP_DIVIDER

PEN_UP_POSITION = 0
PEN_UP_SPEED = 150
PEN_UP_DELAY = 0

PEN_DOWN_POSITION = 75
PEN_DOWN_SPEED = 150
PEN_DOWN_DELAY = 0

ACCELERATION = 1000
MAX_VELOCITY = 1600
CORNER_FACTOR = 0.001

JOG_ACCELERATION = 1600
JOG_MAX_VELOCITY = 1600

VID_PID = '1A86:7523' #Eleksdraw CH314 VID:PID

def find_port():
    for port in comports():
        if VID_PID in port[2]:
            return port[0]
    return None

class DeviceGCODE(object):
    def __init__(self, **kwargs):
        self.slowpen = False
        self.steps_per_unit = STEPS_PER_INCH
        self.pen_up_position = PEN_UP_POSITION
        self.pen_up_speed = PEN_UP_SPEED
        self.pen_up_delay = PEN_UP_DELAY
        self.pen_down_position = PEN_DOWN_POSITION
        self.pen_down_speed = PEN_DOWN_SPEED
        self.pen_down_delay = PEN_DOWN_DELAY
        self.acceleration = ACCELERATION
        self.max_velocity = MAX_VELOCITY
        self.corner_factor = CORNER_FACTOR
        self.jog_acceleration = JOG_ACCELERATION
        self.jog_max_velocity = JOG_MAX_VELOCITY

        for k, v in kwargs.items():
            setattr(self, k, v)

        self.error = (0, 0) # accumulated step error

        port = find_port()
        if port is None:
            raise Exception('cannot find eleksdraw device')
        self.serial = Serial(port, baudrate=BAUDRATE ,timeout=None)

        print('Fond port, waiting headers')
        while not self.serial.in_waiting:
            pass
        while self.serial.in_waiting:
            header = self.readline()
            if len(header) > 0:
                print('Header founded: ' + header)
        self.configure()

    def configure(self):
        self.unlock()
        self.command('M3 S100') # Pen up
        self.pen_up()
        self.home()
        input("Insert pen and press Enter")
        self.command('G21') # Set mm
        # self.command('G91') # Incremental mode
        self.command('G90') # Absolute mode
        # servo_min = 7500
        # servo_max = 28000
        # pen_up_position = self.pen_up_position / 100
        # pen_up_position = int(
        #     servo_min + (servo_max - servo_min) * pen_up_position)
        # pen_down_position = self.pen_down_position / 100
        # pen_down_position = int(
        #     servo_min + (servo_max - servo_min) * pen_down_position)
        # self.command('SC', 4, pen_up_position)
        # self.command('SC', 5, pen_down_position)
        # self.command('SC', 11, int(self.pen_up_speed * 5))
        # self.command('SC', 12, int(self.pen_down_speed * 5))

    def close(self):
        self.serial.close()

    def make_planner(self, jog=False):
        a = self.acceleration
        vmax = self.max_velocity
        cf = self.corner_factor
        if jog:
            a = self.jog_acceleration
            vmax = self.jog_max_velocity
        return Planner(a, vmax, cf)

    def readline(self):
        return str(self.serial.readline().decode("utf-8").rstrip())

    def command(self, *args, cr=True):
        line = ' '.join(map(str, args)) + ( "\r" if cr else "")
        self.serial.write((line).encode('utf-8'))
        # print("Command written: " + line)
        ans = self.readline()
        if ans.startswith("[MSG:"):
            # print("MSG found: " + ans)
            ans = self.readline()
        # print("Ans found: " + ans)
        return ans

    # higher level functions
    def move(self, dx, dy):
        self.run_path([(0, 0), (dx, dy)])

    def goto(self, x, y, jog=True):
        # TODO: jog if pen up
        px, py = self.read_position()
        self.run_path([(px, py), (x, y)], jog)

    def home(self):
        self.command('$H')

    def unlock(self):
        self.command('$X')

    # misc commands
    def version(self):
        # return self.command('V')
        return "Not implemented"

    # motor functions
    def enable_motors(self):
        # m = MICROSTEPPING_MODE
        # return self.command('EM', m, m)
        print("Not implemented call to: enable_motors")
        return "Not implemented"

    def disable_motors(self):
        # return self.command('EM', 0, 0)
        print("Not implemented call to: disable_motors")
        return "Not implemented"

    def motor_status(self):
        # response = self.command('?')
        # response = response.split('|')[0]
        # return response
        # return self.command('QM')
        return "Not implemented"

    def zero_position(self):
        # return self.command('CS')
        return "Not implemented"

    def read_position(self):
        response = self.command('?',cr=False)
        response = response.split('|')[1].split(':')[1].split(',')
        return float(response[0]), float(response[1])

    def stepper_move(self, duration, x, y):
        # px,py = self.read_position()
        # distance = sqrt((x-px)**2+(y-py)**2)
        # velocity = 60*distance/duration # mm/min
        # velocity = velocity if velocity <= 7000 else 7000
        velocity = 7000
        return self.command('G1', 'X%.2f' % x, 'Y%.2f' % y, 'F%.2f' % velocity)

    def wait(self):
        while '1' in self.motor_status():
            time.sleep(0.01)

    def run_plan(self, plan):
        step_ms = TIMESLICE_MS
        step_s = step_ms / 1000
        t = 0
        while t < plan.t:
            i1 = plan.instant(t)
            i2 = plan.instant(t + step_s)
            # print(i2)
            d = i2.p.sub(i1.p)
            ex, ey = self.error
            ex, sx = modf(d.x * self.steps_per_unit + ex)
            ey, sy = modf(d.y * self.steps_per_unit + ey)
            self.error = ex, ey
            self.stepper_move(step_s, i2.p.x, i2.p.y)

            # self.stepper_move(step_ms, int(sx), int(sy))
            t += step_s
        # self.wait()

    def run_path(self, path, jog=False):
        planner = self.make_planner(jog)
        plan = planner.plan(path)
        self.run_plan(plan)

    def run_drawing(self, drawing, progress=True):
        print('number of paths : %d' % len(drawing.paths))
        print('pen down length : %g' % drawing.down_length)
        print('pen up length   : %g' % drawing.up_length)
        print('total length    : %g' % drawing.length)
        print('drawing bounds  : %s' % str(drawing.bounds))
        self.pen_up()
        position = (0, 0)
        bar = Bar(drawing.length, enabled=progress)
        for path in drawing.paths:
            jog = [position, path[0]]
            self.run_path(jog, jog=True)
            bar.increment(path_length(jog))
            self.pen_down()
            self.run_path(path)
            self.pen_up()
            position = path[-1]
            bar.increment(path_length(path))
        bar.done()
        self.run_path([position, (0, 0)], jog=True)

    def plan_drawing(self, drawing):
        result = []
        planner = self.make_planner()
        for path in drawing.all_paths:
            result.append(planner.plan(path))
        return result

    # pen functions
    def pen_position(self):
        response = self.command('?',cr=False)
        response = response.split('|')[2].split(':')[1].split(',')[1]
        return float(response)

    def setPenvelocity(self,slow):
        self.slowpen = slow

    def pen_up(self):
        # delta = abs(self.pen_up_position - self.pen_down_position)
        # duration = int(delta / self.pen_up_speed)
        # delay = max(0, duration + self.pen_up_delay)
        ans = self.command('S%d' % self.pen_up_position)
        time.sleep(0.3)
        return ans
        # return self.command('SP', 1, delay)

    def pen_down(self):
        # delta = abs(self.pen_up_position - self.pen_down_position)
        # duration = int(1000 * delta / self.pen_down_speed)
        # delay = max(0, duration + self.pen_down_delay)
        if self.slowpen :
            N= 10
            for i in [75*x/N for x in range(0,N+1)]:
                ans = self.command("S"+str(i))
                time.sleep(0.1)
        else:
            ans = self.command('S%d' % self.pen_down_position)
        time.sleep(0.1)
        return ans
        # return self.command('SP', 0, delay)

