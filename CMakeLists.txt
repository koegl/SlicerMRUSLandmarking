cmake_minimum_required(VERSION 3.13.4)

project(SlicerMRUSLandmarking)

#-----------------------------------------------------------------------------
# Extension meta-information
set(EXTENSION_HOMEPAGE "https://github.com/koegl/SlicerMRUSLandmarking")
set(EXTENSION_CATEGORY "Informatics")
set(EXTENSION_CONTRIBUTORS "Fryderyk Kögl (TUM, BWH), Harneet Cheema (BWH, UOttawa), Tina Kapur (BWH)")
set(EXTENSION_DESCRIPTION "SlicerMRUSLandmarking is a Slicer extension that provides a user interface focused on landmarking MR and US images.")
set(EXTENSION_ICONURL "https://github.com/koegl/SlicerMRUSLandmarking/raw/main/misc/icon.png")
set(EXTENSION_SCREENSHOTURLS "https://github.com/koegl/SlicerMRUSLandmarking/raw/main/misc/GUIpreview.png")
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
