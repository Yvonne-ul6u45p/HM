# Installation for HM16.22

    # Directory Structure
    /HM16.22
        /codes
        /HM
        check.py
        Readme.md

#### First of all remove the directory HM/ and clone the github page from [this site](https://vcgit.hhi.fraunhofer.de/jvet/HM/-/tree/master?ref_type=heads)

    git clone https://vcgit.hhi.fraunhofer.de/jvet/HM.git
    
#### Install HM16.22

    cd HM/
    
    mkdir build
    cd build
    cmake .. -DCMAKE_BUILD_TYPE=Release
    cmake .. -DCMAKE_BUILD_TYPE=Debug
    make -j
    # any error message shouldn't pop out !
    
#### Check if install successfully ?
    
    cd ..         # jump out of build/
    cd bin/
    
    ./TAppEncoderStaticd        # There should be some config message
    
    
    cd ..         # jump out of bin/
    ./TAppEncoderStaticd        # It should show NO SUCH COMMAND ERROR !!!
    
#### Add system environment
    
    cd ~    # go to home
    vim .bashrc
    
    
    # add this code at the last line of this file
    export PATH={YOUR_PATH_TO_HM16.22}/HM16.22/HM/bin:$PATH
    
        # For example    export PATH=/home/pc-cluster9/HM16.22/HM/bin:$PATH
    
    
    # Refresh your system environment
    bash
    
    # GO back to HM16.22/HM/ again
    TAppEncoderStaticd            # TYPE This command and config message should be seen