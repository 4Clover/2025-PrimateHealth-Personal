library(readxl)

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


# In both the Demographics and Exposure data, there are 218 rows and 213 unique IDs. The following IDs are 
# duplicate (18FBE, 977FB, B8A0E, BF641, and C9CB4). It is important to note that while the IDs are the same,
# it seems that the other data such as StudyID and age at screen differ. When graphing the Raw_min vs Raw_max 
# by PFTpre_7d_avgPM, I noticed that there seems to be a positive correlation between the raw_min 
# and raw_max when comparing it to PFTpre_7d_avgPM. When graphing the average air pollution exposure 7 days
# before the PFT by StudyID, the graph shows that monkeys who were in StudyID C had higher results 
# with the average air pollution exposure in the 7 days before a primate’s lung function test compared 
# to the monkeys in A or B.


