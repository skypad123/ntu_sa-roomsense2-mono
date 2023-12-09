from manager import ActionManager , TimingController
from threading import Thread

def main(): 
    action_manager = ActionManager()
    timing_controller = TimingController()
    timing_controller.attach(action_manager)
    Thread(target=action_manager.run).start()
    Thread(target=timing_controller.run).start()




main()