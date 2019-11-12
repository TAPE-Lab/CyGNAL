args <- commandArgs(trailingOnly = TRUE)

library(plotly)
library(readr)
library(dplyr)
library(ggplot2)
library(forcats)
library(RColorBrewer)
library(shiny)
library(tidyverse)

#Make sure no_norm is like this and marker_marker, not marker-marker -> check dremi script for populatiog the column itself, although i don't think that will pose a problem here in R

dremi_info <- read_tsv(args)
minx <- min(dremi_info$with_outliers_arcsinh_DREMI_score)
maxx <- max(dremi_info$with_outliers_arcsinh_DREMI_score)

print (unique(dremi_info$marker_x_marker_y))

initial_dremi <- dremi_info %>% ggplot(aes(
                        x=file, y=factor(marker_x_marker_y,
                        levels=rev(unique(marker_x_marker_y))))) + 
                    geom_tile(aes(fill=with_outliers_arcsinh_DREMI_score))
                    


# Define UI for application that draws a histogram
ui <- fluidPage(

    # Application title
    titlePanel("DREMI scores heatmap"),

    sidebarPanel(width=3,
        sliderInput("range",
                    "Slider Range:",
                    step = 0.1,
                    min = floor(minx),
                    max = ceiling(maxx) +1,
                    value = c(minx, maxx)),
        selectInput('in6', 'Select markers', unique(dremi_info$marker_x), multiple=TRUE, selectize=TRUE),
        tags$hr(),
        downloadButton('foo', "Download plot as .pdf")
    ),
    mainPanel(width=9,
        plotlyOutput("trendPlot")
    )
)

# Define server logic required to draw a histogram
server <- function(input, output, session) {

    output$out6 <- renderPrint(input$in6)
    
    output$trendPlot <- renderPlotly({
        if (!is.null(input$in6)) {
            print (summary(dremi_info))
            data_to_plot <- dremi_info %>% filter(str_detect(marker_x_marker_y, input$in6))
            # data_to_plot <- dremi_info %>% filter(marker_x_marker_y %in% input$in6)
            print (data_to_plot)
        }
        else{data_to_plot <- dremi_info}
        
        initial_dremi <- data_to_plot %>% ggplot(aes(
            x=file, y=factor(marker_x_marker_y,
                             levels=rev(unique(marker_x_marker_y))))) + 
            geom_tile(aes(fill=with_outliers_arcsinh_DREMI_score)) +
            labs(fill = "DREMI score")
        
        print(
        ggplotly(initial_dremi + scale_fill_gradient(
            low = "#F6F6F6", high = "#A12014", limits=c(input$range[1], input$range[2]),
            oob = scales::squish, breaks = c(input$range[1], input$range[2]), labels = c(paste('<',input$range[1]), paste('>',input$range[2])),
            guide = guide_colourbar(nbin=100, draw.ulim = FALSE, draw.llim = FALSE, ticks = FALSE)) +
            theme(legend.position="right", legend.direction="vertical", 
                    axis.text.x = element_text(angle = 45, hjust = 1)) + 
            xlab("Condition") + ylab("Markers") +
            ggtitle("DREMI scores heatmap")
            ) %>% layout(height = 800) # %>% layout(height = 1400, width = 1200)
        )
    })
    output$foo <- downloadHandler(
        filename = "dremi_heatmap.pdf",
        content = function(file) {
            ggsave(file, plot = initial_dremi + scale_fill_gradient(
            low = "#F6F6F6", high = "#A12014", limits=c(input$range[1], input$range[2]),
            oob = scales::squish, breaks = c(input$range[1], input$range[2]), labels = c(paste('<',input$range[1]), paste('>',input$range[2])),
            guide = guide_colourbar(nbin=100, draw.ulim = FALSE, draw.llim = FALSE, ticks = FALSE)) +
            theme(legend.position="right", legend.direction="vertical", 
                    axis.text.x = element_text(angle = 45, hjust = 1)) + 
            xlab("Condition") + ylab("Markers") +
            ggtitle("DREMI scores heatmap")
            , device = "pdf")
        }
    )
    session$onSessionEnded(stopApp)
}

# Run the application 
shinyApp(ui = ui, server = server)