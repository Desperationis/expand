---
name: find-next
description: Looks at the project to see what the next logical step is to do for this project, including looking at CHECKLIST.md if it exists, then CLAUDE.md.
---

To find the next logical step:
1. If it exists, do the next step in the CHECKLIST.md file. Do not ask me if I want to complete it, just do it immediately, no questions asked. After you complete this step, cross it out. 
2. If there are unit or integration tests in this project, cross reference them to the code and back. If there a case missing that misses a critical bug, implement it. Otherwise, continue.
3. Look through the description of the project in CLAUDE.md and all of the code. Then make a guess as to what the next logical feature for this program would be. Look at gaps in current features, or be creative and come up with a new feature.
4. For #3, if you are ever trying to make a new feature, think up of several other features and let the user decide. After the user decides, think up of several ways to implement it and let the user decide again.



