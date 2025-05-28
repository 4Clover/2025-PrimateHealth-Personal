<!--
DataLab Project Template

Replace allcaps text with your project details. PROJECT_NAME should be your
project's short name.

On GitHub, name the project repository according to the following format:

YEAR_COLLABORATOR_PROJECT_NAME

The project's Google Drive directory should also follow this format.

In the listing of directories, delete anything that isn't relevant to your
project.
-->

# Joint Primate Lung Function Project

This repository contains code for all collaborators of the Primate Lung Function project.

[top]: #Joint-Primate-Lung-Function-Project

#### Maintainer/Lead:
- _Wesley Brooks_

#### Collaborators:
- _Sabine Hung_
- _Simona Kamat_ 
- _Dillon Mannion_ 
- _Tiffany Yeung_

## Descriptive
* We have several data sets with data collected across various studies. 
* We have been provided with a descriptor key for variable names. 
  * Even with a spreadsheet detailing all this, it is still challenging to manage considering the quantity of variables we are working with. 
* There are far more variables than we know what to do with. 
* Due to the structure and type of data we have, we are placing heavy emphasis on 
  dimensionality reduction. 
* This essentially means we hope to merge relevant predictors 
   to obtain more readable results. 
* We have been told that the “Raw_min”, “Iti_mean”, and “Cti_mean” 
  are a good measure of health, so these will be the response variables we focus on. 
  * “Raw_min” is the minimum resistance of airways across measurement periods. 
  * “Iti_mean” is the mean inertance of tissues across a measurement period. 
  * “Cti_mean” is the mean compliance of tissues across a measurement period.
* Each of us turns in our work to our separate branches and links this work to the corresponding issue where the work was assigned. 
* Our file names do not have specific naming conventions, but we each use relevant wording to clarify and specify the work that we have done for the week.


## Goal
The goal of our project is to try and understand how the air quality in which primates–specifically rhesus macaques 
monkeys–are born and raised in effect their lung function later on in their lives. 

We analyze air quality data from different time periods in the monkeys’ lives 
(gestation, neonatal, infancy, postnatal, PFTpre30d, and PFTpre7d) so that we can hope to find 
reliable trends to help determine relevant predictors for this question.

This could be a launching point for implementing the same studies on humans; knowing which predictors to pay special 
attention to will undoubtedly increase efficiency and save on all resources. Depending on the findings, 
this could be the foundation, and the scientific evidence much air quality and pollution regulations and 
legislation to be implemented are based upon. 

While these are definitely a long way off, thinking about the big 
picture is a good source of motivation for these seemingly unrewarding preprocessing and exploratory phases 
we will primarily be focusing on.

Links:

* [Google Drive][google]

[google]: DRIVE_LINK


## File and Directory Structure [WIP]

> [!IMPORTANT]
>
> Do not commit large files (> 1 MB) to the repository. Upload these to cloud
> storage (such as Google Drive or Box) instead.
>
> When you clone this repository, Git will not necessarily create directories
> that only contain large, untracked files (typically `data/` and `outputs/`).
> Instead you must manually create these directories and download their files
> from cloud storage.

The directory structure for the project is:
```
data/           Data sets
docs/           Supporting documents
models/         Trained and serialized models
notebooks/      Notebooks (`.ipynb`, `.Rmd`, ...)
outputs/        Outputs from the code, including intermediate data sets
reports/        HTML or PDF reports generated from notebooks
└── figures/    Graphics and figures to be used in reporting
src/            Python/Java/... (non-R) source code
R/              R source code
.gitattributes  Paths Git should give special treatment
.gitignore      Paths Git should ignore
LICENSE         License for the project
README.md       This file
```
* The data was stored in a Box folder containing several Microsoft Excel spreadsheets 
on various aspects of the primates including their demographics, biobehavioral, pedigree, and exposure. 
* The data was collected by Christopher Royer, who situated the monkeys in polluted inhalable environments. 
* We received the data cleaned, though we simply had to pick out the variables with numerical values 
to begin our analyses. 
* These Excel spreadsheets were transferred over to RStudio, where we have been 
looking at the data more in-depth through processes such as principal component analysis (PCA) 
and cannonical component analysis (CCA) to create biplots that set variables against one another. 
* One of the takeaways from using PCA was that since the data is so multivariate, 
it is difficult to interpret the principal components. 
* For this reason, we have decided to move onto CCA, 
which rotates the components of both the exposures and responses so that they are 
maximally correlated with each other.


<!--
The files in the `data/` directory are:

```

```
-->

([back to top][top])


## Installation

([back to top][top])


## Contributing

([back to top][top])
