@echo off
REM
REM	A breadth test for the Grooviks Cube, including game_server and animator
REM

REM Start servers
start cmd /T:1F /k "..\..\src\gc\game_server\game_server.py 11111 && sleep 5 && exit"
start cmd /T:4F /k "..\..\src\gc\animator\animator.py 7890 && sleep 5 && exit"

REM Breadth test
@echo on

cube 11111 post gc/games name=thename
cube 11111 get gc/games
cube 11111 get gc/games/1
cube 11111 put gc/games/1/moves/34/R3
cube 11111 get gc/games/1/moves
cube 11111 post gc/quit

sleep 2
curl -s -X POST http://localhost:7890/animator/quit

