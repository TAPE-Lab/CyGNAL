#
# This is a Shiny web application. You can run the application by clicking
# the 'Run App' button above.
#
# Find out more about building applications with Shiny here:
#
#    http://shiny.rstudio.com/
#
library(readr)
library(dplyr)
library(ggplot2)
library(forcats)
library(RColorBrewer)
library(shiny)

emd_info <- read_tsv("input/v1-emd_dremi_htmp/Tests/emd_info.txt")

initial_emd <- emd_info %>% select(2,3,5) %>% ggplot(aes(x=fct_rev(compare_from), y=fct_rev(marker))) + geom_tile(aes(fill=EMD_no_norm_arc))

rng_emd = range(emd_info$EMD_no_norm_arc)

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


TEST <- initial_emd + scale_fill_distiller(
    palette = "RdBu", limits=c(floor(input$range[1]), ceiling(input$range[2])),
    #breaks = c(floor(rng[1]), ceiling(rng[2])),
    oob = scales::squish, guide = guide_colourbar(
        nbin=100, draw.ulim = FALSE,
        draw.llim = FALSE, ticks = FALSE)) +
    theme(legend.position="right", legend.direction="vertical", 
          axis.text.x = element_text(angle = 45, hjust = 1)) + 
    xlab("Cell type") + ylab("Markers") +
    ggtitle("EMD scores heatmap")

# Define UI for application that draws a histogram
ui <- fluidPage(

    # Application title
    titlePanel("Initial test"),

    # Sidebar with a slider input for number of bins 
    sidebarLayout(
        sidebarPanel(
            sliderInput("range",
                        "Slider Range:",
                        min = floor(rng_emd[1]) - 1,
                        max = ceiling(rng_emd[2]) -1,
                        value = c(floor(rng_emd[1]), ceiling(rng_emd[2])))
        ),

        # Show a plot of the generated distribution
        mainPanel(
           plotOutput("distPlot")
        )
    )
)

# Define server logic required to draw a histogram
server <- function(input, output) {
    output$range <- renderPrint({ input$slider2 })
    output$distPlot <- renderPlotly({
        # generate bins based on input$bins from ui.R
        initial_emd <- emd_info %>% select(2,3,5) %>% ggplot(aes(x=fct_rev(compare_from), y=fct_rev(marker))) + geom_tile(aes(fill=EMD_no_norm_arc))
        TEST <- initial_emd + scale_fill_distiller(
            palette = "RdBu", limits=c(floor(input$range[1]), ceiling(input$range[2])),
            #breaks = c(floor(rng[1]), ceiling(rng[2])),
            oob = scales::squish, guide = guide_colourbar(
                nbin=100, draw.ulim = FALSE,
                draw.llim = FALSE, ticks = FALSE)) +
            theme(legend.position="right", legend.direction="vertical", 
                  axis.text.x = element_text(angle = 45, hjust = 1)) + 
            xlab("Cell type") + ylab("Markers") +
            ggtitle("EMD scores heatmap")
        TEST
        # draw the histogram with the specified number of bins
    })
}

# Run the application 
shinyApp(ui = ui, server = server)
