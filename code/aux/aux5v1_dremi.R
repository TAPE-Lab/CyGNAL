args <- commandArgs(trailingOnly = TRUE)
args <- paste(args, collapse=" ") #Collapse paths with spaces to single string

#Packages to use:
list.of.packages <- c("tidyverse", 
                        "RColorBrewer",
                        "shiny",
                        "plotly"
                        )
# check if pkgs are installed already, if not, install automatically:
new.packages <- list.of.packages[!(list.of.packages %in% installed.packages()[,"Package"])]
if(length(new.packages)) install.packages(new.packages, repos = "http://cran.us.r-project.org")
#Load packages
lapply(list.of.packages, require, character.only = TRUE)

#FUTURE WORK: Look into ComplexHeatmap (group similar DREMI patterns)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~DATA SETUP~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
#Make sure no_norm is like this and marker_marker, not marker-marker -> 
#check dremi script for populatiog the column itself, although i don't think that will pose a problem here in R
dremi_info <- read_tsv(args)
minx <- min(dremi_info$with_outliers_arcsinh_DREMI_score)
maxx <- max(dremi_info$with_outliers_arcsinh_DREMI_score)

print (unique(dremi_info$marker_x_marker_y))

initial_dremi <- dremi_info %>% ggplot(aes(
                        x=file_origin, y=factor(marker_x_marker_y,
                        levels=rev(unique(marker_x_marker_y))))) + 
                    geom_tile(aes(fill=with_outliers_arcsinh_DREMI_score))
                    
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#


###############################################################################
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#~UI~#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
###############################################################################

ui <- fluidPage(

    # Application title
    titlePanel("CyGNAL: DREMI heatmap"),

    sidebarPanel(width=3,
        sliderInput("range",
                    "Slider Range:",
                    step = 0.1,
                    min = floor(minx),
                    max = ceiling(maxx) +1,
                    value = c(minx, maxx)),
        selectInput('in6', 'Select markers', unique(dremi_info$marker_x), multiple=TRUE, selectize=TRUE),
        selectInput('in12', 'Select and reorder conditions', unique(dremi_info$file_origin), multiple=TRUE, selectize=TRUE),
        tags$hr(),
        downloadButton('foo', "Download plot as .pdf")
    ),
    mainPanel(width=9,
        plotlyOutput("trendPlot")
    )
)

###############################################################################
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#~Server~#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
###############################################################################

server <- function(input, output, session) {

    output$out6 <- renderPrint(input$in6)
    
    output$trendPlot <- renderPlotly({ #Process input data and make plotly heatmap
        if (!is.null(input$in6) & !is.null(input$in12)) {
            data_to_plot <- dremi_info %>% filter(str_detect(marker_x_marker_y, input$in6)) %>% filter(file_origin %in% input$in12)
            data_to_plot$file_origin <- as.factor(data_to_plot$file_origin) %>% fct_relevel(input$in12)
        }
        else if (!is.null(input$in6) & is.null(input$in12)) {
            data_to_plot <- dremi_info %>% filter(str_detect(marker_x_marker_y, input$in6))
        }
        else if (is.null(input$in6) & !is.null(input$in12)) {
            data_to_plot <- dremi_info %>% filter(file_origin %in% input$in12)
            data_to_plot$file_origin <- as.factor(data_to_plot$file_origin) %>% fct_relevel(input$in12)
        }
        else{data_to_plot <- dremi_info}
        
        initial_dremi <- data_to_plot %>% ggplot(aes(
                                x=file_origin, y=factor(marker_x_marker_y,
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
    output$foo <- downloadHandler( #Download plotly heatmap
        filename = "dremi_heatmap.pdf",
        content = function(file_origin) {
            if (!is.null(input$in6) & !is.null(input$in12)) {
                data_to_plot <- dremi_info %>% filter(str_detect(marker_x_marker_y, input$in6)) %>% filter(file_origin %in% input$in12)
                data_to_plot$file_origin <- as.factor(data_to_plot$file_origin) %>% fct_relevel(input$in12)
            }
            else if (!is.null(input$in6) & is.null(input$in12)) {
                data_to_plot <- dremi_info %>% filter(str_detect(marker_x_marker_y, input$in6))
            }
            else if (is.null(input$in6) & !is.null(input$in12)) {
                data_to_plot <- dremi_info %>% filter(file_origin %in% input$in12)
                data_to_plot$file_origin <- as.factor(data_to_plot$file_origin) %>% fct_relevel(input$in12)
            }
            else{data_to_plot <- dremi_info}
            
            initial_dremi <- data_to_plot %>% ggplot(aes(
                                    x=file_origin, y=factor(marker_x_marker_y,
                                    levels=rev(unique(marker_x_marker_y))))) + 
                                    geom_tile(aes(fill=with_outliers_arcsinh_DREMI_score)) +
                                    labs(fill = "DREMI score")
            
            ggsave(file_origin, plot = initial_dremi + scale_fill_gradient(
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
}

# Run the application 
if (getOption("browser") == "") {
    options(browser="xdg-open")
    print("R encountered an error when identifying your default browser.")
    print("Please manually open in your browser the addres indicated below.")
} #The block below solves the utils::browseURL(appUrl) ERROR present in certain conda/WSL installs

shinyApp(ui = ui, server = server)
