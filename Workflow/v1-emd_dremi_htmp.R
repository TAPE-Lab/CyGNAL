library(readr)
library(dplyr)
library(ggplot2)
library(forcats)
library(RColorBrewer)

emd_info <- read_tsv("input/v1-emd_dremi_htmp/Tests/emd_info.txt")

initial_emd <- emd_info %>% select(2,3,5) %>% ggplot(aes(x=fct_rev(compare_from), y=fct_rev(marker))) + geom_tile(aes(fill=EMD_no_norm_arc))

rng_emd = range(emd_info$EMD_no_norm_arc)
#Once the shiny app is working have a plot showing the distribution of the scores

#scale_fill_gradient2(low="green", mid="lightblue", high="red", #colors in the scale
#                     midpoint=mean(rng),    #same midpoint for plots (mean of the range)
#                     breaks=seq(0,1,0.25), #breaks in the scale bar
#                     limits=c(floor(rng[1]), ceiling(rng[2])))

#scale_fill_distiller(palette = "RdBu", oob = scales::squish, guide = guide_colourbar(nbin=100, draw.ulim = FALSE, draw.llim = FALSE, ticks = FALSE))
#scale_fill_distiller(palette = "RdBu", limits=c(lower, upper), oob = scales::squish, breaks = c(lower, upper), labels = c(lower_s, upper_s), guide = guide_colourbar(nbin=100, draw.ulim = FALSE, draw.llim = FALSE, ticks = FALSE))


RB_emd <- initial_emd + scale_fill_distiller(
        palette = "RdBu", limits=c(floor(rng_emd[1]), ceiling(rng_emd[2])),
        #breaks = c(floor(rng[1]), ceiling(rng[2])),
        oob = scales::squish, guide = guide_colourbar(
                                      nbin=100, draw.ulim = FALSE,
                                      draw.llim = FALSE, ticks = FALSE)) +
  theme(legend.position="right", legend.direction="vertical", 
        axis.text.x = element_text(angle = 45, hjust = 1)) + 
  xlab("Cell type") + ylab("Markers") +
  ggtitle("EMD scores heatmap")
  

#ggplotly(RB_emd)

#SHINY INITIAL TEST
# library(shiny)
# ui <- fluidPage(
#   +     plotlyOutput("plot"),
#   +     verbatimTextOutput("event"))
# server <- function(input, output) {
#     +
#       +     # renderPlotly() also understands ggplot2 objects!
#       +     output$plot <- renderPlotly(RB_emd)
#       +
#         +     output$event <- renderPrint({
#           +         d <- event_data("plotly_hover")
#           +         if (is.null(d)) "Hover on a point!" else d
#           })}
# shinyApp(ui, server)
