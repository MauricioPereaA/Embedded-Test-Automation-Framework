# Testing Automation Framework

DTAF is a tool provided by development and testing team

DTAF has been designe as a framework to be used alognside with PyTest. you can use pip to install the project into your environment and start developing your testing bench control.

See the guides and tutorials to learn how to build, test and distribuite your code between your test benches.

# Guides and FAQ.

## Documentation

DTAFT counts with Sphinx & Autodoc documentation. thanks to this you can build your documentation file as a local interactive website or a static pdf document.
the porject counts with automated scripts for x64 systems to build the documentaiton environment, alternatively you can use pip install -e .[docs] if the script fails for some reason.

### How to build the documentation project?

follow the next steps to replicate the documentation in a local machine. you should rebuild the documentation each time you commit a major version.

1. download the DTAF project into your computer
1. inside the venv folder open a terminal emulator, then, execute the `PY-3.8-Linux-x64-docs.sh` or `PY-3.8-Win-x64-docs.bat` (for windows) file to automatically build the documentation virtual environment and install the framework in live mode.
1. move your cursor to `$PROJECT_FOLDER$/docs/`
1. execute the command `make html` or `make.bat html` if you're on windows
1. The file should build your documentation project automatically. in case something fails, pleas report it throught the issues page.

## How to install

We will shield our project from external interruptions and interferences (assuring repetibility and assuring accuracy) by using virtual environments for development.

### For End users

The ideal workflow will be for you to only focus your efforts into your test bench development and control programm. while we supply you with new releases periodically.

Don't forget that you will need to setupt your project's virtual environemnt to install our software, to avoid external interferences into your development (user configurations, environment variables, etc).

### Live installation (DTAF developers only - From Source).

A live installation will allow you to make modifications to our source code and see them in "real time".

1. Download our source code (only for DTAF project developers)
1. move your terminal cursor to the root of the project's folder (/)
1. inside `venv` create a new python's virtual environment and activate it.
1. execute pip install `-e .`
1. test the installation opening `python` and run `import DTAF`, if the instruction succeedded, congratulations, you have settled up DTAF in live mode.

Real time means that you won't need to install multiple times the package, since pip will redirect the import to the source code folder, don't remove it or you may break your python's environment. if you are not going to continue developing DTAF, first uninstall it within pip, then remove the project from your fs.

## How to report a bug?

1. in a notepad, try to describe the isse you found, describe the small parts of it and identify the probable root cause.
2. go to the issue trakcer within jira, or github (it will deppend on the current leadership of the project) and look for similar issues, or if the same issue is already reported by someone else
3. if it's a closed issue, post a comment with your machine information (OS general description and hardware used in your test bench) the version of the framework you're using and the steps to reproduce the issue to reopen the issue and evaluate the action plan to solve the issue.
4. if it's a new issue, add as much information, related to the issue, as you can find. what devices were running, what states were they, you may find some tools within DTAF for this data recollection.

## How to contribuite to this project?

Contribution and teamwork are the keys to succeess. plan with your team and choose the optimal action plan available.
from here on, we will refer as TimeLine to your Project Management tool (Trello, Jira or KanBan sheet/diagram).

### For team leaders / Project Manager / Project Owners.

You will be in charge of coordination, assigning tasks, features and bug tracking to your team, for this, follow the next steps in your **TimeLine**

1. list all your features, tasks and bugtracks elements in a list, in another document. to keep them safe as you follow this guide, in that list, add descriptions, sub tasks, and abstractions of what the task means, what's needed to be done, and in what order, identify which tasks need to be sequenced for the project to work and what relationship are there between tasks.
2. once you have your tasks ordered in your list, start creating task cards in yout TimeLine, each task will be contained within one of 6 cathegories, To be Assigned (**TBA**), Sopped for the day | Ready to Start(**REST**), work in progress (**WIP**), Ready for Review(**R4R**), Stalled (**STOP**) and completed(**CC**).
3. Tasks to be assigned have no one assigned, nor tags, priorities nor sequence, they're future elements that need to be done, but haven't been evaluated yet. this is your playground as project maanger, where you will add tasks, work the cards, and once you have evaulated it's priority, requirements and other characteristics, you will assign them to people from your team to monitor and fulfill the tasks needed. Add bullet points representing each one of the sub tasks that need ot be accomplished for the task to be considered as R4R.
4. Once a task is assigned, move the card to the REST pile, and notify the assigned personeel via email about the task(s) assigned.
5. Once a card is considered as **R4R**, you will need to assign someone to review the code and integrate their branch into the parent branch. solve the conflicts and run the automatized tests to ensure our **QAS**.
6. if the review succeeded, approve the merge request and move the card to the **CC** pile.
7. in case by a major force, something is stopping the progress on the task for more than 1 day, place the task into the **STOP** pile, for you to know what's happenning and why. once the card is in **STOP**, you will need to get in touch with the person or people assigned to the task regularly until the stalled card is discarded or they can continue. either of you will need to add a small report describing why did the card was moved to **STOP**, when did the card was moved, why the card was moved, and what were the steps to fix the issue and continue with the task.
8. ideally you should never remove a person from te task assignment, but there may be occasions where you need to transfer resposability to another developer, in which case, their name will be assigned inside your TimeLine Framework, and as a comment, for the history for the card, the person's mail who was assigned the task prior to the change.
9. as long as the task is in progress either of you need to move the task to the WIP pile. in some cases either of you will need to move the task back to the REST pile, to indicate other people in the team that they're not currently working on that task. ideally they will be in charg to manage their own tasks in the TimeLine framework, if supported.
10. If the task ir rejected in **R4R**, reasign the developer as main responsible of the task and make sure that the code reviewer gave a formal review, on why didn't the task succeeded the review. it has to be specific report and straight to the point.

### For Developers.

You will focus on the task ahead, work in teams, participe in meetings and follow the action plan.
This also means that you will bee in the front line of the project; adding features, fixing bugs and implementing **QAS** into our project, to ease your work, follow the next steps for a better coordination with your team.

1. As developer, you will be assigned tasks, stored within the TimeLine, the TL will describe the task and provide an action item list, defining what will be considered as required characteristics for you to be able to move the task into **C4C**
2. whenever you make a change in the project, limit your changes to your module, if for some reason your change requiers another upde in another module of the project, get in touch with your tl to coordinate the effort and see if someone else is working with one of the modules you will need to change.
3. daily, you will need to move, between **REST** and **WIP** piles, **REST** when you finished working on the task, **WIP** as long as you're working.
4. If for some reason you can't continue with your task, for more than a day, move the task to the **STOP** pile, get in touch with your TL and add a report on why did you moved the task to STOP, when, what are the reasons you can't continue, for you and your team to be able to meet and decide an action plan to follow.
5. If you're assigned as Code Reviewer, (**R4R**) for someone's else task, take in count that you will need to run all test successfully, verify with pre-commit the branch, to ensure our code quality and verify that each one of the action items is really fullfiled as needed.

# How to use our framework?

You can read our documentation for examples, API and a complete list of Features.

# External Requirements.

## Windows.

Download and install Microsoft Visual C++ Build Tools v>=14.0 from https://visualstudio.microsoft.com/visual-cpp-build-tools/. then select the Visual Studio Tools >=2022. **but not the installation bundle,** instead; go to the "individual packages" tab, and select the following:

1. C ++ v >= 14 (x86 and x64).
1. Windows 10 API.
1. Windows 11 API.

## Linux.

Download and Install build-essentials with your distribution package Manager.
