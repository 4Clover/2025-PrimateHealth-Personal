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

# -----------------------------------------------------------
