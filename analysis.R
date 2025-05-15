#### joint analysis
### rhesus macaque -- primate lung function##

## set working directories
# SIMONA
# setwd("/Users/simona/Downloads/")
# SABINE
# setwd("/Users/sabinehung/sts195/")
# TIFFANY
# setwd("~/Downloads/royer_primate_health/")


## loading packages
library(ggplot2)
library(readxl)
library(dplyr)
library(lattice)
library(reshape2)
library(ggcorrplot)
library(vegan)
library(colourvalues)
library(corrr)
library(FactoMineR)
library(factoextra)
library(corrplot)
library(tourr)




## read in data
exposure = read_excel("predictor_exposure.xlsx")
pedigree = read_excel("predictor_pedigree.xlsx")
demographics = read_excel("PFT_demographics.xlsx")
biobehavior = read_excel("predictor_biobehavior.xlsx")


combined = merge(exposure, demographics, by = c("ID", "StudyID", "Sex"))


# ---------- exploratory ----------

dim(demographics)
str(demographics)
summary(demographics)
length(unique(demographics$ID)) 
table_IDs <- table(demographics$ID)
duplicate_IDs <- table_IDs[table_IDs > 1]
duplicate_IDs

dim(exposure)
str(exposure)
summary(exposure)
length(unique(exposure$ID)) 

dim(pedigree)
str(pedigree)
summary(pedigree)
length(unique(pedigree$offspringID))

dim(combined)
str(combined)
summary(combined)
length(unique(combined$ID)) 


ggplot(combined, aes(x = Raw_min, y = Raw_max, color = PFTpre_7d_avgPM)) +
  geom_point() +
  labs(title = "Raw_min vs Raw_max colored by PFTpre_7d_avgPM",
       x = "Raw_min",
       y = "Raw_max",
       color = "PFTpre_7d_avgPM") +
  theme_minimal()

ggplot(exposure, aes(x = StudyID, y = PFTpre_7d_avgPM)) +
  geom_boxplot() +
  labs(title = "Average Air Pollution Exposure 7 Days Before PFT by StudyID", x = "StudyID", y = "PFTpre_7d_avgPM") +
  theme_minimal()

summary(combined)

fivenum(combined$Raw_max)
fivenum(combined$Raw_min)
fivenum(combined$PFTpre_7d_avgPM)

plot(combined$Raw_min, combined$Raw_max)
abline(lm(combined$Raw_max ~ combined$Raw_min))

plot(combined$Raw_min, combined$PFTpre_7d_avgPM)

plot(combined$Raw_max, combined$PFTpre_7d_avgPM)

num_combined = combined %>% 
  select(where(is.numeric))
corr_mat <- round(cor(num_combined), 2)
melted = melt(corr_mat)
ggplot(melted, aes(x = Var1, y = Var2, fill = value)) +
  geom_tile()

ggcorrplot(corr_mat)


# ---------- PCA ----------

num_combined = combined[sapply(combined, is.numeric)]
str(num_combined)

# no missing data
colSums(is.na(num_combined))
# scale data before PCA -- normalization
combined_scaled = scale(num_combined)
dim(combined_scaled)


non_num = combined_scaled[, -which(apply(combined_scaled, 2, var) !=0)]
ncol(non_num)
colnames(non_num)

# remove said columns from the data we ultimately do PCA on
combined_scaled = combined_scaled[, which(apply(combined_scaled, 2, var) !=0)]
# 218, 154
dim(combined_scaled)

colnames(combined_scaled)

exposure_PCA = princomp(combined_scaled)
summary(exposure_PCA)

# loadings tell you how much each variable contributes to a particular principal 
# component (correlation between the variable and the principal component)
exposure_PCA$loadings[, 1:10]


# plot the scree plot (indicates how much of the data is explained by the first, 
# second, third, ... principal component
fviz_screeplot(exposure_PCA, addlabels = TRUE)

#' The first 10 components account for 74.2% of the explained variance.

# principal component analysis results for variables
var <- get_pca_var(exposure_PCA)
var
# coordinates for the variables
var$coord
# correlations between variables and dimensions
var_correlation = data.frame(var$cor)

# cos2 for the variables
var$cor2

# contributions of the variables
# provides us with a quantitative measure of the importance of each variable to 
# our principal components
var_contributions = data.frame(var$contrib)

fviz_pca_ind(exposure_PCA,
             col.ind = "cos2", # Color by the quality of representation
             gradient.cols = c("#00AFBB", "#E7B800", "#FC4E07"),
             repel = TRUE     # Avoid text overlapping
)


# positive correlated vars point in same direction
# negative correlated vars point in opposite direction
fviz_pca_var(exposure_PCA,
             col.var = "contrib", # Color by contributions to the PC
             gradient.cols = c("#00AFBB", "#E7B800", "#FC4E07"),
             repel = TRUE     # Avoid text overlapping
)


# plot where points fall on the first two principal components, with arrows representing columns in the original data.
# biplot(exposure_PCA)

fviz_pca_biplot(exposure_PCA, repel = TRUE, 
                col.var = "#2E9FDF", # Variables color
                col.ind = "#696969"  # Individuals color
)

# Eigenvalues
eig.val <- get_eigenvalue(exposure_PCA)
eig.val
eig.val[1:10,]

# Results for Variables
res.var <- get_pca_var(exposure_PCA)
res.var$coord          # Coordinates
res.var$contrib        # Contributions to the PCs
res.var$cos2           # Quality of representation 

# Results for individuals
res.ind <- get_pca_ind(exposure_PCA)
res.ind$coord          # Coordinates
res.ind$contrib        # Contributions to the PCs
res.ind$cos2           # Quality of representation 


fviz_contrib(exposure_PCA, choice = 'var', axes = 1)
fviz_contrib(exposure_PCA, choice = 'var', axes = 2)
fviz_contrib(exposure_PCA, choice = 'var', axes = 3)
fviz_contrib(exposure_PCA, choice = 'var', axes = 4)
fviz_contrib(exposure_PCA, choice = 'var', axes = 5)
fviz_contrib(exposure_PCA, choice = 'var', axes = 6)
fviz_contrib(exposure_PCA, choice = 'var', axes = 7)
fviz_contrib(exposure_PCA, choice = 'var', axes = 8)
fviz_contrib(exposure_PCA, choice = 'var', axes = 9)
fviz_contrib(exposure_PCA, choice = 'var', axes = 10)


# ----------CCA ----------
# break exposures into groups
gest = select(exposure, starts_with("gest"))
neonatal = select(exposure, starts_with("neonatal"))
infancy = select(exposure, starts_with("infancy"))
postnatal = select(exposure, starts_with("postnatal"))

y = as.matrix(combined[, c("Raw_mean", "Iti_mean", "Cti_mean")])
num_combined = combined[sapply(combined, is.numeric)]


# Postnatal group without BW_zscore and AgeAtScreen
X_postnatal_1 = select(combined, starts_with("postnatal"), -contains("totalhours"), -contains("nanCount"), -contains("AUC"),
                       -contains("count"))
X_postnatal_matrix = as.matrix(X_postnatal_1)

res_postnatal_1 <- CCorA(X_postnatal_matrix, y)
biplot(res_postnatal_1, xlab = '')

# Postnatal group with BW_zscore and AgeAtScreen
X_postnatal_2 = select(combined, BW_zscore, AgeAtScreen, starts_with("postnatal"), -contains("totalhours"), -contains("nanCount"), -contains("AUC"),
                       -contains("count"))
X_postnatal_matrix_2 = as.matrix(X_postnatal_2)

res_postnatal_2 <- CCorA(X_postnatal_matrix_2, y)
biplot(res_postnatal_2, xlab = '')

# Gestational group without BW_zscore and AgeAtScreen
X1_df = select(combined, starts_with("gest"), -contains("totalhours"), -contains("nanCount"), -contains("AUC"),
               -contains("count"))
X1 = as.matrix(X1_df)

res_vegan <- CCorA(X1, y)
X1_scores <- res_vegan$Cx
Y1_scores <- res_vegan$Cy

biplot(res_vegan)

# Gestational group with BW_zscore, AgeAtScreen

X2_df = select(combined, BW_zscore, AgeAtScreen, starts_with("gestational"), -contains("totalhours"), -contains("nanCount"), -contains("AUC"),
               -contains("count"))
X2 = as.matrix(X2_df)

res_vegan_2 <- CCorA(X2, y)
X2_scores <- res_vegan$Cx
Y1_scores <- res_vegan$Cy

biplot(res_vegan_2)

gest = gest[, which(apply(gest, 2, var) !=0)]
gest

res_vegan_1 <- CCorA(gest, y)
gest_scores <- res_vegan_1$Cx
y_scores <- res_vegan_1$Cy
res_vegan_1


# neonatal group without BW_zscore and AgeAtScreen

exp = exposure[, which(apply(exposure, 2, var) !=0)] |>
  # don't take columns with basic counts 
  select(-contains(c("totalhours", "nanCount", "AUC", "count")))

neonatal = select(exp, starts_with("neonatal"))
neonatal_cca <- CCorA(neonatal, y)
neonatal_scores <- neonatal_cca$Cx
y_scores_2 <- neonatal$Cy
neonatal_cca

neonatal_rez <- CCorA(y, neonatal)
biplot(neonatal_rez, xlab = '')

# neonatal group with BW_zscore and AgeAtScreen

neonatal_2 = select(combined, BW_zscore, AgeAtScreen, starts_with("neonatal"), -contains(c("totalhours", "nanCount", "AUC", "count")))
neonatal_2_rez <- CCorA(y, neonatal_2)
biplot(neonatal_2_rez, xlab = '')
