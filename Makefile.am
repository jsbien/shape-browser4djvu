bin_PROGRAMS = revealshapes

revealshapes_SOURCES = \
    revealshapes.cpp \
    libdjvu/DjVuDocument.cpp \
    libdjvu/DjVmDir.cpp \
    libdjvu/GContainer.cpp \
    libdjvu/GException.cpp \
    libdjvu/GMapAreas.cpp \
    libdjvu/GOS.cpp \
    libdjvu/GRect.cpp \
    libdjvu/GSmartPointer.cpp \
    libdjvu/ByteStream.cpp \
    libdjvu/DataPool.cpp \
    libdjvu/DjVuDumpHelper.cpp \
    libdjvu/DjVuFile.cpp \
    libdjvu/DjVuImage.cpp \
    libdjvu/DjVuMessageLite.cpp \
    libdjvu/DjVuPort.cpp \
    libdjvu/DjVuText.cpp \
    libdjvu/DjVuToPS.cpp \
    libdjvu/GBitmap.cpp \
    libdjvu/GURL.cpp \
    libdjvu/IFFByteStream.cpp \
    libdjvu/XmlParser.cpp

# Include local headers from libdjvu and external
AM_CPPFLAGS = -Ilibdjvu -Iexternal

# C++20 standard and threading flags
AM_CXXFLAGS = $(PTHREAD_CFLAGS) -std=c++2a

# Link with system DjVuLibre
revealshapes_LDADD = -ldjvulibre
