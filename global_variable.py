'''
    Copyright (C) <2019>  <natureofnature>

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
'''

screen_size_x = 1920 
screen_size_y = 1080 
mouse_press_position_x = 0
mouse_press_position_y = 0
def set_mouse_press_position(x,y):
    mouse_press_position_x = x
    mouse_press_position_y = y 



def get_mouse_press_position():
    return mouse_press_position_x,mouse_press_position_y

def set_screen_size(x,y):
    screen_size_x = x
    screen_size_y = y

def get_screen_size():
    return screen_size_x,screen_size_y

