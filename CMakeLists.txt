cmake_minimum_required(VERSION 3.13.4)

project(Landmarking View)

#-----------------------------------------------------------------------------
# Extension meta-information
set(EXTENSION_HOMEPAGE "https://www.slicer.org/wiki/Documentation/Nightly/Extensions/LandmarkingView")
set(EXTENSION_CATEGORY "Annotations")
set(EXTENSION_CONTRIBUTORS "Fryderyk Kögl (TUM, Harvard)")
set(EXTENSION_DESCRIPTION "An extension for improved data visualisation for adding landmarks")
set(EXTENSION_ICONURL "http://www.example.com/Slicer/Extensions/LandmarkingView.png")
set(EXTENSION_SCREENSHOTURLS "http://www.example.com/Slicer/Extensions/LandmarkingView/Screenshots/1.png")
set(EXTENSION_DEPENDS "NA") # Specified as a list or "NA" if no dependencies

#-----------------------------------------------------------------------------
# Extension dependencies
find_package(Slicer REQUIRED)
include(${Slicer_USE_FILE})

#-----------------------------------------------------------------------------
# Extension modules
add_subdirectory(LandmarkingView)
## NEXT_MODULE

#-----------------------------------------------------------------------------
include(${Slicer_EXTENSION_GENERATE_CONFIG})
include(${Slicer_EXTENSION_CPACK})
