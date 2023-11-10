library(dplyr)
library(tidyr)
library(purrr)
library(stringr)
library(understandBPMN)

# model <- file.choose()

models <- c(list.files("../BPMN/LowLevel", ".bpmn", full.names = T),
            list.files("../BPMN/LPM", "LPM.bpmn", full.names = T),
            list.files("../BPMN/Massimiliano", "Massimiliano.bpmn", full.names = T))

compute <- function(model, print_out = FALSE) {
  # model <- str_replace(model, "..", "C:/Users/lucp10279/Documents/.git/eventabstraction/Collab Padua")

  weight <- understandBPMN::cognitive_weight(model, signavio = F)
  if(print_out) { print(weight) }

  # Dimension 1 - Token Behaviour Complexity
  split <- understandBPMN::token_split(model, signavio = F)
  if(print_out) { print(paste("Token Split:", split)) }

  conhet <- understandBPMN::connector_heterogeneity(model, signavio = F)
  if(print_out) { print(paste("Connector heterogeneity:", conhet)) }

  # Dimension 2 - Node IO Complexity
  cfc <- control_flow_complexity(model, signavio = F)
  if(print_out) { print(paste("Control flow complexity:", cfc)) }

  seq <- understandBPMN::sequentiality(model, signavio = F)
  if(print_out) { print(paste("Sequentiality:", seq)) }

  # Dimension 3 - Path Complexity - Mostly diameter
  # cyc <- understandBPMN::cyclicity(model, F)
  # if(print_out) { print(paste("Cyclicity:", cyc)) }
  #
  # dia <- understandBPMN::diameter(model, F)
  # if(print_out) { print(paste("Diameter:", dia)) }
  #
  # depth <- understandBPMN::depth(model, F)
  # if(print_out) { print(paste("Depth:", depth)) }

  # Dimension 4 - Degree of Connectedness
  dens <- understandBPMN::density_process_model(model, signavio = F)
  if(print_out) { print(paste("Density:", dens)) }

  cnc <- understandBPMN::coefficient_network_connectivity(model, F)
  if(print_out) { print(paste("Coefficient network connectivity:", cnc)) }

  result <- data.frame(id = model,
                       cognitive_weight = weight,
                       token_split = split,
                       connector_heterogeneity = conhet,
                       control_flow_complexity = cfc,
                       sequentiality = seq,
                       # cyclicity = cyc,
                       # diameter = dia,
                       # depth = depth,
                       density = dens,
                       coefficient_network_connectivity = cnc)

  return(result)
}

output <- list_along(models)

i = 0

pb <- winProgressBar(max = length(models), label = "Complexity")

for(model in models) {
  i <- i + 1
  # print(paste("\n", model, ": Iteration", i))
  output[[i]] <- compute(model, print_out = FALSE)
  perc = i / length(models)
  setWinProgressBar(pb, i, label = paste0(round(perc*100, 2), "% complete"))
}

close(pb)

output <- bind_rows(output) %>%
  mutate(id = str_replace(id, "../BPMN/", "")) %>%
  separate(col = id, into = c("level", "id"), sep = "/") %>%
  select(id, level, everything()) %>%
  arrange(id, level)

write.csv(output, "complexity.csv", row.names = F)


# df <- df %>% mutate(data = map(model, compute))
