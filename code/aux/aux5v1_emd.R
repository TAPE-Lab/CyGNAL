args <- commandArgs(trailingOnly = TRUE)
args <- paste(args, collapse=" ") #Collapse paths with spaces to single string

#Packages to use:
list.of.packages <- c("tidyverse", 
                        "RColorBrewer",
                        "shiny",
                        "plotly",
                        "ComplexHeatmap"
                        )
# check if pkgs are installed already, if not, install automatically:
new.packages <- list.of.packages[!(list.of.packages %in% installed.packages()[,"Package"])]
if(length(new.packages)) install.packages(new.packages, repos = "http://cran.us.r-project.org")
#Load packages
lapply(list.of.packages, require, character.only = TRUE)


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~DATA SETUP~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
#Change selection to one based on col position (select from dplyr)
emd_info <- read_tsv(args)
minx <- min(emd_info %>% select(1))
maxx <- max(emd_info %>% select(1))

print(minx, maxx)
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

###############################################################################
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#~UI~#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
###############################################################################
# Define UI for application that draws a histogram
ui <- fluidPage(

    # Application title
    titlePanel("CyGNAL: EMD heatmap"),

    sidebarLayout(
        sidebarPanel(width=4,
            sliderInput("range",
                        "Slider Range: (only for Plotly heatmap",
                        step = 0.1,
                        min = floor(minx) - 1,
                        max = ceiling(maxx) +1,
                        value = c(minx, maxx)),
            selectInput('in6', 'Select markers', unique(emd_info$marker), multiple=TRUE, selectize=TRUE),
            selectInput('in12', 'Select and reorder conditions', unique(emd_info$file_origin), multiple=TRUE, selectize=TRUE),
            tags$hr(),
            downloadButton('foo', "Download plotly Heatmap as .pdf"),
            downloadButton("complex", "Download annotated ComplexHeatmap as .pdf")
        ),
        mainPanel(
            tabsetPanel(
                tabPanel("Plotly plot", width=8, plotlyOutput("trendPlot")),
                tabPanel("Complex Heatmap",height = "800px",plotOutput("complexheatmap"))
            )
        )
    )


)

###############################################################################
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#~Server~#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
###############################################################################
# Define server logic required to draw a histogram
server <- function(input, output, session) {

    output$out6 <- renderPrint(input$in6)
    
    output$trendPlot <- renderPlotly({
        if (!is.null(input$in6) & !is.null(input$in12)) {
            data_to_plot <- emd_info %>% filter(marker %in% input$in6) %>% filter(file_origin %in% input$in12)
            data_to_plot$file_origin <- as.factor(data_to_plot$file_origin) %>% fct_relevel(input$in12)
        }
        else if (!is.null(input$in6) & is.null(input$in12)) {
            data_to_plot <- emd_info %>% filter(marker %in% input$in6)
        }
        else if (is.null(input$in6) & !is.null(input$in12)) {
            data_to_plot <- emd_info %>% filter(file_origin %in% input$in12) 
            data_to_plot$file_origin <- as.factor(data_to_plot$file_origin) %>% fct_relevel(input$in12)
        }
        else{data_to_plot <- emd_info}
        # saveRDS(data_to_plot, "testdata.RDS")
        initial_emd <- data_to_plot %>% ggplot(aes(x=file_origin, y=fct_rev(marker))) + geom_tile(aes(fill=EMD_no_norm_arc))
        print(
        ggplotly(initial_emd + scale_fill_distiller(
            palette = "RdBu", limits=c(input$range[1], input$range[2]),
            #breaks = c(floor(rng[1]), ceiling(rng[2])),
            oob = scales::squish, guide = guide_colourbar(
                nbin=100, draw.ulim = FALSE,
                draw.llim = FALSE, ticks = FALSE)) +
            theme(legend.position="right", legend.direction="vertical", 
                    axis.text.x = element_text(angle = 45, hjust = 1)) + 
            xlab("Condition") + ylab("Markers") +
            ggtitle("EMD scores heatmap")
        ) %>% layout(height = 700, width = 700))
    })
    output$complexheatmap <- renderPlot({ ###TESTING ADDITION OF COMPLEXHEATMAP###
        if (!is.null(input$in6) & !is.null(input$in12)) {
            data_to_plot <- emd_info %>% filter(marker %in% input$in6) %>% filter(file_origin %in% input$in12)
            data_to_plot$file_origin <- as.factor(data_to_plot$file_origin) %>% fct_relevel(input$in12)
        }
        else if (!is.null(input$in6) & is.null(input$in12)) {
            data_to_plot <- emd_info %>% filter(marker %in% input$in6)
        }
        else if (is.null(input$in6) & !is.null(input$in12)) {
            data_to_plot <- emd_info %>% filter(file_origin %in% input$in12) 
            data_to_plot$file_origin <- as.factor(data_to_plot$file_origin) %>% fct_relevel(input$in12)
        }
        else{data_to_plot <- emd_info}
        df <- data_to_plot %>% select(EMD_no_norm_arc, file_origin, marker) %>% spread(marker,EMD_no_norm_arc)
        conditions <- df$file_origin
        df_mat <- df %>% select(-file_origin) %>% as.matrix()
        rownames(df_mat) <- conditions
        Heatmap(t(df_mat), name="EMD scores", column_title="Conditions",row_title="Markers",column_names_rot=60)
    }, width=600, height=800)

    output$foo <- downloadHandler(
        filename = "emd_heatmap.pdf",
        content = function(file) {
            if (!is.null(input$in6) & !is.null(input$in12)) {
                data_to_plot <- emd_info %>% filter(marker %in% input$in6) %>% filter(file_origin %in% input$in12)
                data_to_plot$file_origin <- as.factor(data_to_plot$file_origin) %>% fct_relevel(input$in12)
            }
            else if (!is.null(input$in6) & is.null(input$in12)) {
                data_to_plot <- emd_info %>% filter(marker %in% input$in6)
            }
            else if (is.null(input$in6) & !is.null(input$in12)) {
                data_to_plot <- emd_info %>% filter(file_origin %in% input$in12) 
                data_to_plot$file_origin <- as.factor(data_to_plot$file_origin) %>% fct_relevel(input$in12)
            }
            else{data_to_plot <- emd_info}
            
            initial_emd <- data_to_plot %>% ggplot(aes(x=file_origin, y=fct_rev(marker))) + geom_tile(aes(fill=EMD_no_norm_arc))
            
            ggsave(file, plot = initial_emd + scale_fill_distiller(
                                palette = "RdBu", limits=c(input$range[1], input$range[2]),
                #breaks = c(floor(rng[1]), ceiling(rng[2])),
                                oob = scales::squish, guide = guide_colourbar(
                                    nbin=100, draw.ulim = FALSE,
                                    draw.llim = FALSE, ticks = FALSE)) +
                            theme(legend.position="right", legend.direction="vertical", 
                                axis.text.x = element_text(angle = 45, hjust = 1)) +  #, aspect.ratio = 1)) +
                            xlab("Condition") + ylab("Markers") +
                    ggtitle("EMD scores heatmap")
            , device = "pdf")
        }
    )
    output$complex <- downloadHandler(
        filename = "emd_complexheatmap.pdf",
        content = function(file) {
            if (!is.null(input$in6) & !is.null(input$in12)) {
                data_to_plot <- emd_info %>% filter(marker %in% input$in6) %>% filter(file_origin %in% input$in12)
                data_to_plot$file_origin <- as.factor(data_to_plot$file_origin) %>% fct_relevel(input$in12)
            }
            else if (!is.null(input$in6) & is.null(input$in12)) {
                data_to_plot <- emd_info %>% filter(marker %in% input$in6)
            }
            else if (is.null(input$in6) & !is.null(input$in12)) {
                data_to_plot <- emd_info %>% filter(file_origin %in% input$in12) 
                data_to_plot$file_origin <- as.factor(data_to_plot$file_origin) %>% fct_relevel(input$in12)
            }
            else{data_to_plot <- emd_info}
            
            df <- data_to_plot %>% select(EMD_no_norm_arc, file_origin, marker) %>% spread(marker,EMD_no_norm_arc)
            conditions <- df$file_origin
            df_mat <- df %>% select(-file_origin) %>% as.matrix()
            rownames(df_mat) <- conditions
            pdf(file)#Had to save using general method and calling draw() to heatmap
            draw(Heatmap(t(df_mat), name="EMD scores", column_title="Conditions",row_title="Markers",column_names_rot=60)) #, heatmap_height=unit(16,"cm") apply to draw call to modify height
            dev.off()
        }
    )
    #session$onSessionEnded(stopApp)
}

# Run the application 

if (getOption("browser") == "") {
    options(browser="xdg-open")
    print("R encountered an error when identifying your default browser.")
    print("Please manually open in your browser the addres indicated below.")
} #The block below solves the utils::browseURL(appUrl) ERROR present in certain conda/WSL installs

shinyApp(ui = ui, server = server) #, options = list(launch.browser=TRUE))
