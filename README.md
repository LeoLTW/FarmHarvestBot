# FarmHarvestBot

# Purpose

we hope that we can reduce the intensive- labor work in farm. So we want to use robot-arm and object detection to replace human being.


# Technique

Object detection:
We use yolo with pytorch. this decision is concerned about the model size and accuracy.

If the model is too big, the calculation will take time. 

In the other way, if it is too small, it might let the accuray down. So, yolo would be the perfect fit in this project.


Robot-arm:
Our demo Robot-arm is Braccio.

It's a simple arm-type with 6 motor that we can control. 

Although,there is a limitation of angle, we still think it's function is enough for this project.

But, yes, if we want to improve this project, we definetly need a more powerful robot-arm.
