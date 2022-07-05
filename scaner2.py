import pygame
import pygame_gui
import cv2
import sys
import requests
import io
import datetime
import ftplib
import configparser
import logging
import os
import logging

from requests.auth import HTTPDigestAuth
from PIL import Image

import scaner_gui

#configparser
config = configparser.ConfigParser()
config.read('config.cnf')
#logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', filename='log')
logging.info('==============')
logging.info('start programm')


#if no folden, then create folder
if not os.path.exists(config.get('OTHER_CONFIG', 'folder_for_screenshots')):
        os.mkdir(config.get('OTHER_CONFIG', 'folder_for_screenshots'))

def enter_key(code):
    ##
    datetime_now = datetime.datetime.now()
    screenshot_name = code+'_'+str(datetime_now.year)+'-'
    #date
    if datetime_now.month<10:
        screenshot_name += '0'+str(datetime_now.month)+'-'
    else:
        screenshot_name += str(datetime_now.month)+'-'
    if datetime_now.day<10:
        screenshot_name += '0'+str(datetime_now.day)+'_'
    else:
        screenshot_name += +str(datetime_now.day)+'_'
    #time
    if datetime_now.hour<10:
        screenshot_name += '0'+str(datetime_now.hour)
    else:
        screenshot_name += str(datetime_now.hour)
    if datetime_now.minute<10:
        screenshot_name += '0'+str(datetime_now.minute)
    else:
        screenshot_name += str(datetime_now.minute)
    if datetime_now.second<10:
        screenshot_name += '0'+str(datetime_now.second)+'_'
    else:
        screenshot_name += str(datetime_now.second)+'_'
    screenshot_name += config.get('OTHER_CONFIG', 'workplace')
    ##
    try:
        screenshot = requests.get(
            'http://'+config.get('IP_CAMERA', 'cam_adress')+'/cgi-bin/snapshot.cgi',
            params={'channel': '1'},
            auth=auth_for_camera)
    except:
        logging.error('error screenshot')
        return False
    try:
        image = Image
        img = image.open(io.BytesIO(screenshot.content))
        img.save('screenshots/'+screenshot_name+'.jpg')
    except:
        logging.error('error save screenshot')
        return False
    try:
        ftp = ftplib.FTP('192.168.40.30', 'ftpkamery', 'alamakota123')
        file_to_upload = open(config.get('OTHER_CONFIG', 'folder_for_screenshots')+'/'+screenshot_name+'.jpg', 'rb')
        ftp.storbinary('STOR '+config.get('FTP_SERVER', 'ftp_folder')+screenshot_name+'.jpg', file_to_upload)
        ftp.close()
    except:
        logging.error('error ftp')
        return False
    return True

screen_width = config.getint('OTHER_CONFIG', 'screen_width')#1366
screen_height = config.getint('OTHER_CONFIG', 'screen_height')#768

auth_for_camera = HTTPDigestAuth(config.get('IP_CAMERA', 'cam_login'), config.get('IP_CAMERA', 'cam_pass'))

camera = cv2.VideoCapture('rtsp://'+config.get('IP_CAMERA', 'cam_login')+
                          ':'+config.get('IP_CAMERA', 'cam_pass')
                          +'@'+config.get('IP_CAMERA', 'cam_adress')+':554/cam/realmonitor?channel=1&subtype=1')
pygame.init()
pygame.display.set_caption("OpenCV camera stream on Pygame")
screen = pygame.display.set_mode([screen_width, screen_height], pygame.FULLSCREEN)
manager = pygame_gui.UIManager((screen_width, screen_height))

exit_btn_x = 0
exit_btn_y = 0
exit_btn_width = 100
exit_btn_height = 40
button = scaner_gui.Button(exit_btn_x, exit_btn_y, exit_btn_width, exit_btn_height, 'X', manager)

console_width = config.getint('OTHER_CONFIG', 'console_width')#300
console_height = config.getint('OTHER_CONFIG', 'console_height')#250

console = pygame_gui.windows.UIConsoleWindow(
    rect=pygame.rect.Rect((screen_width-console_height, screen_height-console_width), (console_height, console_width)),
    manager=manager)
manager.set_focus_set(console.command_entry)
##
clock = pygame.time.Clock()

error = False
timer_for_rectangle = 0
try:
    while True:
        ret, frame = camera.read()

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = frame.swapaxes(0, 1)
        frame = cv2.resize(frame, (screen_height, screen_width))

        time_delta = clock.tick(60)/1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit(0)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    sys.exit(0)
            ##
            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == button.button:
                    sys.exit(0)
            ##
            if (event.type == pygame_gui.UI_CONSOLE_COMMAND_ENTERED and
                    event.ui_element == console):
                command = event.command
                if command != '':
                    if enter_key(command):
                        errors = False
                    else:
                        errors = True
                    timer_for_rectangle = config.getint('OTHER_CONFIG', 'status_timer')
                    print(command)
                    console.disable()
            manager.process_events(event)
        manager.update(time_delta)
        pygame.surfarray.blit_array(screen, frame)
        manager.draw_ui(screen)
        if timer_for_rectangle > 0:
            if errors == False:
                pygame.draw.rect(screen, (0, 255, 0), pygame.Rect(2, exit_btn_height, exit_btn_width-4, 40))
            else:
                pygame.draw.rect(screen, (255, 0, 0), pygame.Rect(30, 30, 60, 60))
            timer_for_rectangle -= 1
            if timer_for_rectangle == config.getint('OTHER_CONFIG', 'status_timer') - 20:
                console.enable()
                manager.set_focus_set(console.command_entry)
        pygame.display.update()
except (KeyboardInterrupt, SystemExit):
    pygame.quit()
    cv2.destroyAllWindows()
