# Flipbook page footer for dissertation

## General information

- Name: Erik Fritz
- Institution: TNO Wind Energy, Delft University of Technology
- Email: e.fritz@tno.nl

## Description
This repository contains files to create a flipbook-like page footer for a book. In my case, a rotating wind turbine whose blades slowly evolve from straight to swept as you go through my dissertation.

## Versions
1. 31.07.24: Initial upload
2. 17.11.2025: Added a Python version of the Matlab code and additional code for a spar-type floating wind turbine with waves and heave motion (Deepali)


## File overview
- **turbinePlanform.dat**: Contains the planform data required to plot a wind turbine blade. The three columns are the spanwise position, the chord length and the relative position of the pitch axis. The planform is based on the [IEA 15 MW reference wind turbine](https://github.com/IEAWindTask37/IEA-15-240-RWT).
- **RunFlipbookPageFooter.m**: The Matlab scripts used to create the animated page footer. Loads the data from **turbinePlanform.dat** and creates a plot for each frame, which are temporarily saved as individual pdf files. The script then pulls all individual frame pdf files into a single pdf where every page contains one frame.
- **append_pdfs.m**: Is a Matlab community function developed by Oliver Woodford ([append_pdfs - File Exchange - MATLAB Central (mathworks.com)](https://nl.mathworks.com/matlabcentral/fileexchange/31215-append_pdfs), accessed 25.03.22). The function is used to append all individual frames of the flipbook into one pdf.
- **FlipbookPageFooter.pdf**: Is the pdf file created by **RunFlipbookPageFooter.m**, which contains the flipbook with one frame per page.
- **DemoDocument.tex**: Is a demo latex document, in which the page footer is applied. The footer on every right page contains the page from **FlipbookPageFooter.pdf** with the page number identical to the page number of the latex document. This way, the page footer becomes a flipbook, if the pages of **FlipbookPageFooter.pdf** form a flipbook.

- **DemoDocument.pdf**: Is the pdf file created by **DemoDocument.tex**.
- **flipbook_floater_spar.py**: Is the equivalent python script without any sweep, but with added lines to include a heave motion, spar buoy geometry, and a wave pattern.

   
