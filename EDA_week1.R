######################### Import and Load Packages #############################
packages <- c("ggplot2", "readxl", "skimr", "GGally")
missing_packages <- packages[!sapply(packages, requireNamespace, quietly = TRUE)]
if (length(missing_packages) > 0) {
  install.packages(missing_packages)
} else {
  remove(missing_packages, packages)
}
library(ggplot2)
library(readxl)
library(skimr)
library(GGally)

################################ Load Data #####################################
demographic_data <- read_excel("./PFT_demographics.xlsx")
fire_exposure_data <- read_excel("./predictor_exposure.xlsx")
#parent_data <- read_excel("../predictor_pedigree.xlsx")
#behavior_data <- read_excel("../predictor_biobehavior.xlsx")

########################### Univariate Analysis ################################
# 1. Counts and summaries
summary(demographic_data)
# BW_zscore has a very high max of 4.59 which is likely an outlier, highly improbable so also error?
# possible outliers in EC150 -- max 32

# 2. Missing values
skim(demographic_data)
# nothing of note, data is clean

# 3. Distribution
ggplot(numeric_demographic_data, aes(Raw_mean)) + geom_histogram()
# left skew for Raw_mean -- from younger population?
### to be CONTINUED... ###

# 4. Outliers
### to be CONTINUED... ###

########################### Multivariate Analysis #############################
# 1. Correlation
numeric_demographic_data <- demographic_data[sapply(demographic_data, is.numeric)]
ggcorr(numeric_demographic_data, method = c("all.obs",  "spearman") ,label = TRUE, label_alpha = TRUE, label_size = 3, label_color = "black", hjust = 0.75, size = 3, layout.exp = 1)
# pos. correlations of note:
# a. BW & BW_bin && cti(not std) seem to be correlated ~ 0.7
# b. BW & BW_bin && Raw_mean seem to be correlated ~ 0.7
# c. law_max && Raw_mean,max,min seem to be correlated ~ 0.8

# neg. correlations of note:
# a. Btube && Raw_mean, law_max, Raw_max, Raw_min  ~ -0.7/0.8
# b. Bti* && Cti_mean ~ -1
# c. lti && ResNorm show lots of neg. correlations ~ -0.6/0.7



############################## Conclusion ###################################

# Findings indicate that the data is clean and no missing values of note were found within demographic_data.
# The correlation matrix shows that there are some strong positive correlations between certain variables.
# Particulars of note are (BW and BW_bin), as well as between (law_max and Raw_mean).
# Negative correlations are also notable between (Btube and Raw_mean, law_max, Raw_max, Raw_min) and (Bti* and Cti_mean).
# The left skew of the Raw_mean histogram suggests something, still need to explore and perform the same on the other variables.
# The next step is to perform the same analysis on the other datasets (fire_exposure_data, parent_data, behavior_data) and compare the results.
# I may possibly use a categorical route for analysis as discussed in our last meeting, and see if the groupings present in the heat maps follow the same trends.