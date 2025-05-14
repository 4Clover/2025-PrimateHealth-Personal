# joint analysis

# Simona ---------------------------

data = read_excel('/Users/simona/Downloads/PFT_demographics.xlsx')

head(data)

str(data)
summary(data)

nrow(data)

length(unique(data$ID)) 


table_IDs <- table(data$ID)

duplicate_IDs <- table_IDs[table_IDs > 1]

duplicate_IDs

library(ggplot2)


pred_data = read_excel('/Users/simona/Downloads/predictor_exposure.xlsx')

head(pred_data)

str(pred_data)
summary(pred_data)

nrow(pred_data)

length(unique(pred_data$ID)) 

combined <- merge(data, pred_data, by = "ID")

ggplot(combined, aes(x = Raw_min, y = Raw_max, color = PFTpre_7d_avgPM)) +
  geom_point() +
  labs(title = "Raw_min vs Raw_max colored by PFTpre_7d_avgPM",
       x = "Raw_min",
       y = "Raw_max",
       color = "PFTpre_7d_avgPM") +
  theme_minimal()

ggplot(pred_data, aes(x = StudyID, y = PFTpre_7d_avgPM)) +
  geom_boxplot() +
  labs(title = "Average Air Pollution Exposure 7 Days Before PFT by StudyID", x = "StudyID", y = "PFTpre_7d_avgPM") +
  theme_minimal()



demographic <- read_excel("/Users/simona/Downloads/PFT_demographics.xlsx")
exposure <- read_excel("/Users/simona/Downloads/predictor_exposure.xlsx")

combined_df = left_join(demographic, exposure)

y = as.matrix(combined_df[, c("Raw_mean", "Iti_mean", "Cti_mean")])

# 1. Postnatal group without BW_zscore and AgeAtScreen

X_postnatal_1 = select(combined_df, starts_with("postnatal"), -contains("totalhours"), -contains("nanCount"), -contains("AUC"),
                       -contains("count"))
X_postnatal_matrix = as.matrix(X_postnatal_1)

res_postnatal_1 <- CCorA(X_postnatal_matrix, y)
biplot(res_postnatal_1, xlab = '')

# It seems that the iTi_mean and Raw_mean could be a group, as the arrows point in nearly the same direction.

# 2. Postnatal group with BW_zscore and AgeAtScreen

X_postnatal_2 = select(combined_df, BW_zscore, AgeAtScreen, starts_with("postnatal"), -contains("totalhours"), -contains("nanCount"), -contains("AUC"),
                       -contains("count"))
X_postnatal_matrix_2 = as.matrix(X_postnatal_2)

res_postnatal_2 <- CCorA(X_postnatal_matrix_2, y)
biplot(res_postnatal_2, xlab = '')

# Sabine -----------------------------------------------------------

library(openxlsx)

PFT_demographic = read_excel("/Users/sabinehung/sts195/PFT_demographics.xlsx")
predictor_exposure = read_excel("/Users/sabinehung/sts195/predictor_exposure.xlsx")
predictor_pedigree = read_excel("/Users/sabinehung/sts195/predictor_pedigree.xlsx")
predictors_description = read_excel("/Users/sabinehung/sts195/predictors_description.xlsx")

# Interpret the Data

#' IMPORTANT (from Adventures in Data Science, 8. Data Visualization )
#'    Good Data Visualizations = provide rapid access to data, faithfully
#'        represent the data and tell a story, expressive, effective
#'    Bad Data Visualizations = too much or too little information, inconsistent,
#'        ignore limits of human perception, misrepresent the data, use
#'        inappropriate or garbage data

#'  BRAINSTORMING
#'  1. What is the average body weight for males/females?
#'  2. What is the relationship between 'Raw_std' vs 'Rti_std'?

#' General outline of 'PFT_demographic' data
#' Working with tidy data?
#' 1. Each observation has its own row. yes
#' 2. Each feature has its own column. yes
#' 3. Each value has its own cell. yes
#' Things to Note
#'    PFT = pulmonary function test
#'    Raw = resistance in the airway
#'    Rti = resistance of tissues
#'    Cti = compliance of tissues
#'    Iti = intertance of tissues
#'    Eti = mean elastance of tissues
ncol(PFT_demographic) # number of columns = 37
nrow(PFT_demographic) # number of rows = 218
colnames(PFT_demographic)
summary(PFT_demographic)

# 1. What is the correlation among 'Cti_std' vs 'Rti_std' vs 'Iti_std'?
cor(PFT_demographic[c("Cti_std", "Rti_std", 'Iti_std')]) 
#' corr btwn Cti_std vs Rti_std = 0.4153503
#' corr btwn Cti_std vs Iti_std = 0.1238057
#' corr btwn Rti_std vs Iti_std = 0.5231102

# 2. What is the correlation among 'Cti_mean' vs 'Rti_mean' vs 'Iti_mean' vs 'Eti'?
cor(PFT_demographic[c("Cti_mean", "Rti_mean", 'Iti_mean', 'Eti')]) 
#' corr btwn Cti_mean vs Rti_mean = -0.3091232
#' corr btwn Cti_mean vs Iti_mean = -0.1076574
#' corr btwn Cti_mean vs Eti = -0.6813732
#' corr btwn Rti_mean vs Iti_mean = 0.1111173
#' corr btwn Rti_mean vs Eti = 0.5033897
#' corr btwn Iti_mean vs Eti = 0.2127782

# 3. VISUALIZATION: What is the relationship between 'Raw_min' and 'Raw_max'?
ggplot(PFT_demographic) + aes(x = Raw_min, y = Raw_max) + geom_point()

# General outline of 'predictor_exposure' data
#' Working with tidy data?
#' 1. Each observation has its own row. yes
#' 2. Each feature has its own column. yes
#' 3. Each value has its own cell. yes
#' Things to Note
#'    gestational
#'    neonatal = newborn, first 30 days of life
#'    infancy
#'    postnatal
ncol(predictor_exposure) # number of columns = 129
nrow(predictor_exposure) # number of rows = 218
summary(predictor_exposure)

#' 4. VISUALIZATION: What do the relationships between 'gest_avgPM', 'gest_avgO3'
#'    'gest_avgNO2' look like?
library("ggplot2")
# gest_avgPM vs gest_avgO3
ggplot(predictor_exposure) + aes(x = gest_avgPM, y = gest_avgO3) + geom_point()
# gest_avgNO2 vs gest_avgO3
ggplot(predictor_exposure) + aes(x = gest_avgNO2, y = gest_avgO3) + geom_point()
# gest_avgNO2 vs gest_avgPM
ggplot(predictor_exposure) + aes(x = gest_avgNO2, y = gest_avgPM) + geom_point()

# 5. VISUALIZATION: Mass plots on different categories
plot(predictor_exposure[,1:12]) # gest_nanCount
plot(predictor_exposure[,22:33]) # neonatal_nanCount
plot(predictor_exposure[,47:52]) # infancy_count

# Tiffany -----------------------------------------------------------
