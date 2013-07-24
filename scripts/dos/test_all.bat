@echo off
REM
REM	A breadth test for the Grooviks Cube, including game_server and animator
REM

REM Start servers
call .\start.bat

REM Breadth test
@echo on

cube 11111 post gc/games name=thename
cube 11111 get gc/games
cube 11111 get gc/games/1
cube 11111 put gc/games/1/moves/34/R3
cube 11111 get gc/games/1/moves
cube 11111 delete gc


