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
    
    cd ../bin/                # jump into bin/
    ./TAppEncoderStaticd      # There should be some config message
    
                                # jump out of bin/
    ../TAppEncoderStaticd       # It should show NO SUCH COMMAND ERROR !!!
                                # bash: ../TAppEncoderStaticd: No such file or directory
    
#### Add system environment
    echo 'export PATH=/home/pc-cluster{num}/HM16.22/HM/bin:$PATH' >> ~/.bashrc
    
    vim ~/.bashrc
    # add this code at the last line of this file
    export PATH=/home/pc-cluster{num}/HM16.22/HM/bin:$PATH

#### Check
    # Refresh your system environment
    bash
    
    cd ~/HM16.22/HM/            # GO back to ~/HM16.22/HM/ again
    TAppEncoderStaticd          # TYPE This command and config message should be seen
