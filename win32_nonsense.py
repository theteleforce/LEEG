import constants as c
import logging
import win32api as win32
import win32con as winc


# In order to make my life easier, I'm going to assume we only have two monitors
# There's no obvious way to extend this to n monitors, since you'd somehow have to
# store a choice of what monitor to switch to. Any suggestions would be much appreciated.
def swap_monitors():
    monitor_handle_list = win32.EnumDisplayMonitors()
    # live dangerously, kids
    # if len(monitor_handle_list) != 2:
    #    raise ValueError("[FATAL] Detected {} monitors (swap only works with 2 monitors)".format(len(monitor_handle_list)))
    if len(monitor_handle_list) == 1:
        raise ValueError("[FATAL] Only detected 1 monitor. What are you doing?")
    elif len(monitor_handle_list) > 2:
        print("Detected {} monitors. Asusming the first two are the intended two...", len(monitor_handle_list))
    
    monitor_0_info = win32.GetMonitorInfo(monitor_handle_list[0][0])
    monitor_1_info = win32.GetMonitorInfo(monitor_handle_list[1][0])
    new_primary_monitor = monitor_1_info if monitor_0_info['Flags'] & c.PRIMARY_MONITOR_I_THINK else monitor_0_info

    for monitor_info in [monitor_0_info, monitor_1_info]:
        device_settings = win32.EnumDisplaySettings(DeviceName=monitor_info['Device'], ModeNum=winc.ENUM_CURRENT_SETTINGS)
        device_settings.Position_x = monitor_info['Monitor'][0] - new_primary_monitor['Monitor'][0]
        device_settings.Position_y = monitor_info['Monitor'][1] - new_primary_monitor['Monitor'][1]

        flags = winc.CDS_UPDATEREGISTRY | winc.CDS_NORESET
        if monitor_info == new_primary_monitor:
            flags |= winc.CDS_SET_PRIMARY
        change_status = win32.ChangeDisplaySettingsEx(DeviceName=monitor_info['Device'], DevMode=device_settings, Flags=flags)
        if change_status != winc.DISP_CHANGE_SUCCESSFUL:
            logging.error("[FATAL] Failed to switch monitors: ChangeDisplaySettingsEx for monitor {} returned failure code {}".format(monitor_info['Device'], change_status))
            raise ValueError("[FATAL] Failed to switch monitors: ChangeDisplaySettingsEx for monitor {} returned failure code {}".format(monitor_info['Device'], change_status))

    commit_status = win32.ChangeDisplaySettingsEx() # an empty CDSE 'commits' the changes
    if commit_status != winc.DISP_CHANGE_SUCCESSFUL:
        logging.error("[FATAL] Failed to switch monitors: NULL ChangeDisplaySettingsEx returned failure code {}".format(commit_status))
        raise ValueError("[FATAL] Failed to switch monitors: NULL ChangeDisplaySettingsEx returned failure code {}".format(commit_status))


if __name__ == '__main__':
    swap_monitors()  # for testing purposes
