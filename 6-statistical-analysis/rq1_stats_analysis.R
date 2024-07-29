# Clear the environment
rm(list=ls())

# Download the required libraries if not installed
if (!require("exact2x2")) install.packages("exact2x2")
if (!require("xtable")) install.packages("xtable")
if (!require("effsize")) install.packages("effsize")
if (!require("nortest")) install.packages("nortest")

# Load the required libraries
library(exact2x2)
library(xtable)
library(effsize)
library(nortest)

data<-read.csv("rq1_results_filtered.csv")

# Init the list of results
res=list(lng1 = c(), lng2 = c(), model = c(), p.value = c(), OR = c())

languages=c('java', 'py', 'jl', 'lua', 'r', 'rkt')
models=c('codellama-7b', 'codellama-13b', 'deepseek-1.3b', 'deepseek-6.7b', 'deepseek-33b', 'copilot')

# Loop over each language, for each model
for (lng1 in languages) {
  for (lng2 in languages) {
    for (model in models) {
      if (lng1 != lng2 & !any(res$lng1 == lng2 & res$lng2 == lng1 & res$model == model)) {
        # Load the data
        lng1_pass=data[which(data["language"]==lng1 & data["model"]==model),]$pass
        lng2_pass=data[which(data["language"]==lng2 & data["model"]==model),]$pass
        
        # McNemar test
        mn=mcnemar.exact(lng2_pass,lng1_pass)
        p.value=mn$p.value
        or=mn$estimate
        
        res$lng1=c(res$lng1,lng1)
        res$lng2=c(res$lng2,lng2)
        res$model=c(res$model,model)
        res$p.value=c(res$p.value,p.value)
        res$OR=c(res$OR,or)
      }
    }
    # Adjust p-values for each pair of languages, considering all models
    res$p.value[which(res$lng1 == lng1 & res$lng2 == lng2)]= p.adjust(res$p.value[which(res$lng1 == lng1 & res$lng2 == lng2)], method = "BH")
  }
}

# Generate the dataframes and export to csv
res=data.frame(res)

# Sort dataframe in the following order: lng1, lng2, model: [deepseek-1.3b, deepseek-6.7b, deepseek-33b, codellama-7b, codellama-13b]
res=res[order(res$lng1, res$lng2, match(res$model, c('deepseek-1.3b', 'deepseek-6.7b', 'deepseek-33b', 'codellama-7b', 'codellama-13b'))),]
write.csv(res, file = "rq1_stats_analysis.csv")