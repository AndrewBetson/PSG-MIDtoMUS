pyinstaller --name MIDtoMUS --onefile -F ^
	--add-binary bsutils/tarcman.exe:bsutils ^
	--add-binary bsutils/WAVInterleaver.exe:bsutils ^
	src/main.py src/binio.py src/mus.py
