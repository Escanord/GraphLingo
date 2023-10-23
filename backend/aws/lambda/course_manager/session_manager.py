import json

class SessionManager:
    def __init__(self, attributes):
        # CHECKING STEPS
        if('session_manager' not in attributes):
            manager_attributes = {
                'step': 0
            }
        else:
            print(attributes)
            manager_attributes = json.loads(attributes['session_manager'])
        
        self.step = manager_attributes['step']
    
    def increment(self):
        self.step += 1
        
    def checkStepAndIncrement(self, step):
        if(self.onStep(step)):
            self.increment()
            return True
        return False
    
    def patchAttributes(self, attributes):
        patch = json.dumps({
                'step': self.step,
            })
        
        attributes['session_manager'] = patch
        return attributes
    
    def onStep(self, step):
        return step == self.step
    
    def setStep(self, step):
        self.step = step