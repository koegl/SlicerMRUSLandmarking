cmake_minimum_required(VERSION 3.13.4)

project(SlicerMRUSLandmarking)

#-----------------------------------------------------------------------------
# Extension meta-information
set(EXTENSION_HOMEPAGE "https://www.slicer.org/wiki/Documentation/Nightly/Extensions/SlicerMRUSLandmarking")
set(EXTENSION_CATEGORY "Annotations")
set(EXTENSION_CONTRIBUTORS "Fryderyk Kögl (TUM, BWH)")
set(EXTENSION_DESCRIPTION "An extension for improved data visualisation for adding landmarks")
set(EXTENSION_ICONURL "http://www.example.com/Slicer/Extensions/SlicerMRUSLandmarking.png")
set(EXTENSION_SCREENSHOTURLS "http://www.example.com/Slicer/Extensions/SlicerMRUSLandmarking/Screenshots/1.png")
set(EXTENSION_DEPENDS "NA") # Specified as a list or "NA" if no dependencies

#-----------------------------------------------------------------------------
# Extension dependencies
find_package(Slicer REQUIRED)
include(${Slicer_USE_FILE})

#-----------------------------------------------------------------------------
# Extension modules
add_subdirectory(SlicerMRUSLandmarking)
## NEXT_MODULE

#-----------------------------------------------------------------------------
include(${Slicer_EXTENSION_GENERATE_CONFIG})
include(${Slicer_EXTENSION_CPACK})
