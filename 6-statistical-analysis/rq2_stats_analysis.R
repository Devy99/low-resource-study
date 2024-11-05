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

data<-read.csv("rq2_results.csv")

# Init the list of results
res=list(technique1 = c(), technique2 = c(), lng = c(), model = c(), p.value = c(), OR = c())

languages=c('r', 'rkt')
models=c('codellama-7b', 'codellama-13b', 'deepseek-1.3b', 'deepseek-6.7b', 'deepseek-33b', 'copilot')
techniques=c('baseline', 'icl-rules', 'icl-translation', 'icl-fewshot', 'finetune', 'pretrain-finetune')

# Loop over
for (technique1 in techniques) {
  for (technique2 in techniques) {
    for (lng in languages) {
      for (model in models) {
        # If model is Copilot and one of the techniques is finetune-type, skip
        if (model == 'copilot' & (technique1 == 'finetune' | technique2 == 'finetune' | technique1 == 'pretrain-finetune' | technique2 == 'pretrain-finetune')) {
          next
        }
        if (technique1 != technique2 & !any(res$technique1 == technique2 & res$technique2 == technique1 & res$lng == lng & res$model == model)) {
          # Load the data
          technique1_pass=data[which(data["language"]==lng & data["model"]==model & data["technique"]==technique1),]$pass
          technique2_pass=data[which(data["language"]==lng & data["model"]==model & data["technique"]==technique2),]$pass
                
          # McNemar test
          mn=mcnemar.exact(technique2_pass,technique1_pass)
          p.value=mn$p.value
          or=mn$estimate
          
          res$technique1=c(res$technique1,technique1)
          res$technique2=c(res$technique2,technique2)
          res$lng=c(res$lng,lng)
          res$model=c(res$model,model)
          res$p.value=c(res$p.value,p.value)
          res$OR=c(res$OR,or)
        }
      }
    }
    # Adjust p-values for each pair of techniques, considering all languages and models
    res$p.value[which(res$technique1 == technique1 & res$technique2 == technique2)]= p.adjust(res$p.value[which(res$technique1 == technique1 & res$technique2 == technique2)], method = "BH")
  }
}

# Generate the dataframes and export to csv
res=data.frame(res)

# Sort dataframe by lng_model_technique_cmp
res=res[order(res$technique1, res$technique2, res$lng, match(res$model, c('deepseek-1.3b', 'deepseek-6.7b', 'deepseek-33b', 'codellama-7b', 'codellama-13b'))),]
write.csv(res, file = "rq2_stats_analysis.csv")