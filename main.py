# ////////////////////////////////////////////////////////////////
# //                     IMPORT STATEMENTS                      //
# ////////////////////////////////////////////////////////////////

import math
import sys
import time

from kivy.app import App
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.graphics import *
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.uix.slider import Slider
from kivy.uix.image import Image
from kivy.uix.behaviors import ButtonBehavior
from kivy.clock import Clock
from kivy.animation import Animation
from functools import partial
from kivy.config import Config
from kivy.core.window import Window
from pidev.kivy import DPEAButton
from pidev.kivy import PauseScreen
from time import sleep
import RPi.GPIO as GPIO
from pidev.stepper import stepper
from pidev.Cyprus_Commands import Cyprus_Commands_RPi as cyprus
from kivy.properties import ObjectProperty
# ////////////////////////////////////////////////////////////////
# //                      GLOBAL VARIABLES                      //
# //                         CONSTANTS                          //
# ////////////////////////////////////////////////////////////////
START = True
STOP= False
UP = False
DOWN = True
ON = True
OFF = False
tall_OFF = False
short_OFF = False
HOME = True
homeDirection = 0


YELLOW = .180, 0.188, 0.980, 1
BLUE = 0.917, 0.796, 0.380, 1
CLOCKWISE = 0
COUNTERCLOCKWISE = 1
ARM_SLEEP = 2.5
DEBOUNCE = 0.10

lowerTowerPosition = 60
upperTowerPosition = 76

position = 0


# ////////////////////////////////////////////////////////////////
# //            DECLARE APP CLASS AND SCREENMANAGER             //
# //                     LOAD KIVY FILE                         //
# ////////////////////////////////////////////////////////////////
class MyApp(App):

    def build(self):
        self.title = "Robotic Arm"
        return sm


Builder.load_file('main.kv')
Window.clearcolor = (.1, .1, .1, 1)  # (WHITE)

cyprus.open_spi()

# ////////////////////////////////////////////////////////////////
# //                    SLUSH/HARDWARE SETUP                    //
# ////////////////////////////////////////////////////////////////

sm = ScreenManager()
arm = stepper(port=0, speed=10)
cyprus.initialize()
cyprus.setup_servo(2)


# ////////////////////////////////////////////////////////////////
# //                       MAIN FUNCTIONS                       //
# //             SHOULD INTERACT DIRECTLY WITH HARDWARE         //
# ////////////////////////////////////////////////////////////////

class MainScreen(Screen):
    version = cyprus.read_firmware_version()
    #Slider.value = 0
    lastClick = time.clock()
    #Slider.value = ObjectProperty(None)
    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)
        self.initialize()

    def debounce(self):
        processInput = False
        currentTime = time.clock()
        if ((currentTime - self.lastClick) > DEBOUNCE):
            processInput = True
        self.lastClick = currentTime
        return processInput

    def toggleArmV(self):
        print("Process vertical arm movement here")
        self.setArmPositionV()

    def setArmPositionV(self):
        print("Move arm vertically here")
        global DOWN
        if DOWN:
            cyprus.set_pwm_values(1, period_value=100000, compare_value=100000, compare_mode=cyprus.LESS_THAN_OR_EQUAL)
            print("robotic arm up")
            self.ids.armControl.text = "Raise Arm"
            DOWN = False
        else:
            cyprus.set_pwm_values(1, period_value=100000, compare_value=0, compare_mode=cyprus.LESS_THAN_OR_EQUAL)
            print("robotic arm down")
            self.ids.armControl.text = "Lower Arm"
            DOWN = True

    def toggleArmH(self):
        print("Process horizontal arm movement here")
        self.setArmPositionH()

    def setArmPositionH(self):
        print("Move arm horizontally here")
        global HOME
        global position
        position = self.ids.moveArm.value * -1


        while True:

            if HOME:
                #arm.set_as_home()
                print("arm moving")
                arm.go_to_position(position)
                #print(self.Slider.value)
                print("moved")
                #arm.softStop()

                break
            else:
                arm.goHome()
                print(" now at home")
                HOME = True
                break
        x = self.ids.moveArm.value

       #self.isBallOnTallTower()
        #if tall_OFF == False:

            #arm.start_relative_move(14)
        #else:
           # if short_OFF == False:
          #      arm.start_relative_move(5)



    def toggleMagnet(self):
        print("Process magnet here")
        #talon motor
        self.setMagnet()

    def setMagnet(self):
        global OFF
        if OFF:
            cyprus.set_servo_position(2, 1)
            print("magnet has grabbed")
            self.ids.magnetControl.text = "Magnet Off"
            OFF = False

        else:
            cyprus.set_servo_position(2, 0.5)
            print("magnet has released")
            self.ids.magnetControl.text = "Magnet On"
            OFF = True

    def auto(self):
        print("Run the arm automatically here")

        self.isBallOnTallTower()
        if tall_OFF == False:
            print("ball in on top tower")
            arm.go_to_position(-12)
            cyprus.set_pwm_values(1, period_value=100000, compare_value=100000, compare_mode=cyprus.LESS_THAN_OR_EQUAL)
            print("lowered")
            sleep(0.5)
            cyprus.set_servo_position(2, 1)
            print("grabbed")
            sleep(0.5)
            cyprus.set_pwm_values(1, period_value=100000, compare_value=0, compare_mode=cyprus.LESS_THAN_OR_EQUAL)
            print("raised")
            sleep(0.5)
            arm.go_to_position(-20)
            print("at final location")
            cyprus.set_pwm_values(1, period_value=100000, compare_value=100000, compare_mode=cyprus.LESS_THAN_OR_EQUAL)
            print("lowered")
            sleep(1)
            cyprus.set_servo_position(2, 0.5)
            print("released")
            sleep(0.5)
            cyprus.set_pwm_values(1, period_value=100000, compare_value=0, compare_mode=cyprus.LESS_THAN_OR_EQUAL)
            print("raised")
            sleep(0.5)
            arm.go_to_position(0)



        else:
            self.isBallOnShortTower()
            if short_OFF == False:
                print("ball is at short tower")
                arm.go_to_position(-20)
                cyprus.set_pwm_values(1, period_value=100000, compare_value=100000, compare_mode=cyprus.LESS_THAN_OR_EQUAL)
                print("lowered")
                sleep(0.5)
                cyprus.set_servo_position(2, 1)
                print("grabbed")
                sleep(0.5)
                cyprus.set_pwm_values(1, period_value=100000, compare_value=0,
                                      compare_mode=cyprus.LESS_THAN_OR_EQUAL)
                print("raised")
                sleep(0.5)
                arm.go_to_position(-12)
                print("at final location")
                cyprus.set_pwm_values(1, period_value=100000, compare_value=100000,
                                      compare_mode=cyprus.LESS_THAN_OR_EQUAL)
                print("lowered")
                sleep(1)
                cyprus.set_servo_position(2, 0.5)
                print("released")
                sleep(0.5)
                cyprus.set_pwm_values(1, period_value=100000, compare_value=0, compare_mode=cyprus.LESS_THAN_OR_EQUAL)
                print("raised")
                sleep(0.5)
                arm.go_to_position(0)




    def homeArm(self):
        global homeDirection
        arm.home(1)

    def isBallOnTallTower(self):
        print("Determine if ball is on the top tower")
        global tall_OFF
        if ((cyprus.read_gpio() & 0b0001) == 0):
            print("GPIO on port P6 is LOW")
            tall_OFF = False
        else:
            tall_OFF = True

    def isBallOnShortTower(self):
        print("Determine if ball is on the bottom tower")
        global short_OFF
        if ((cyprus.read_gpio() & 0b0010) == 0):
            print("GPIO on port P7 is LOW")
            short_OFF = False
        else:
            short_OFF = True

    def initialize(self):
        print("Home arm and turn off magnet")
        cyprus.set_servo_position(2, 0.5)
        self.homeArm()


    def resetColors(self):
        self.ids.armControl.color = YELLOW
        self.ids.magnetControl.color = YELLOW
        self.ids.auto.color = BLUE

    def quit(self):
        MyApp().stop()


sm.add_widget(MainScreen(name='main'))

# ////////////////////////////////////////////////////////////////
# //                          RUN APP                           //
# ////////////////////////////////////////////////////////////////

MyApp().run()
cyprus.close_spi()