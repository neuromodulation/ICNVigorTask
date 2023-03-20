Neuro Omega System SDK installation folder includes the following files and folders:

[Installation Directory]
1. ReadMe.txt - Explain the installation folder content.
2. CPP_SDK
3. MATLAB_SDK
4. Win10Pcap - Auto installed when running on windows 10 or latter.

[Installation Directory]\CPP_SDK\Doc
1. Neuro Omega System CPP SDK Manual.pdf - the Neuro Omega System CPP SDK user manual.

[Installation Directory]\CPP_SDK\Example\
1. [Installation Directory]\CPP_SDK\Example\SystemSDKExample - a Microsoft Visual Studio 2010 C++ project example that uses Neuro Omega System CPP SDK.

[Installation Directory]\CPP_SDK\Include
1. [Installation Directory]\Include\AOTypes.h      - Header file that defines data types used by Neuro Omega System CPP SDK.
2. [Installation Directory]\Include\AOSystemAPI.h  - Header file that defines the API of Neuro Omega System CPP SDK.
3. [Installation Directory]\Include\StreamFormat.h - Header file that defines the data stream structures received through Neuro Omega System CPP SDK.
* User should configure the C++ project to look for header files also in this directory. See SystemSDKExample example project.

[Installation Directory]\CPP_SDK\win32
1. [Installation Directory]\CPP_SDK\win32\NeuroOmega.dll - the DLL to copy to the .exe working directory when running win32 application.
2. [Installation Directory]\CPP_SDK\win32\NeuroOmega.lib - the .lib to link with when running win32 application.
3. [Installation Directory]\CPP_SDK\win32\SystemSDKExample.exe - Example project for Neuro Omega System CPP SDK.
* User should configure the C++ project to look for lib files also in this directory. See SystemSDKExample example project.
* User should add the appropriate .lib file to the preprocessor input to call functions from NeuroOmega DLL. See SystemSDKExample example project.

[Installation Directory]\CPP_SDK\win64
1. [Installation Directory]\CPP_SDK\win64\NeuroOmega_x64.dll - the DLL to copy to the .exe working directory when running win64 application.
2. [Installation Directory]\CPP_SDK\win64\NeuroOmega_x64.lib - the .lib to link with when running win64 application.
3. [Installation Directory]\CPP_SDK\win64\SystemSDKExample_x64.exe - Example project for Neuro Omega System CPP SDK.
* User should configure the C++ project to look for lib files also in this directory. See SystemSDKExample example project.
* User should add the appropriate .lib file to the preprocessor input to call functions from NeuroOmega DLL. See SystemSDKExample example project.

[Installation Directory]\MATLAB_SDK\Doc
1. Neuro Omega System MATLAB SDK Manual.pdf - the Neuro Omega System MATLAB SDK user manual.
2. All MATLAB SDK functions - can run on both win32 and win64 MATLAB.
