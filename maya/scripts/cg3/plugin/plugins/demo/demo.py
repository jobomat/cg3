import pymel.core as pc

class MyClass:
    def gui(self, filename, asset):
        result = pc.promptDialog(
            title='Demo Modal',
            text='Blubb',
            message='Enter Anything:',
            button=['OK', 'Cancel'],
            defaultButton='OK',
            cancelButton='Cancel',
            dismissString='Cancel'
        )
        if result != 'OK':
            return
        test_text = pc.promptDialog(query=True, text=True)

def initialize():
    return MyClass
