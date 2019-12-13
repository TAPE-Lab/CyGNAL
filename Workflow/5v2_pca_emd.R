args <- commandArgs(trailingOnly = TRUE)

#Packages to use:
list.of.packages <- c("DT", 
                        "GGally",
                        "psych",
                        "Hmisc",
                        "MASS",
                        "tabplot",
                        "RColorBrewer",
                        "shiny",
                        "tidyverse",
                        "FactoMineR",
                        "factoextra",
                        "matrixStats",
                        "plotly"
                        )
# check if pkgs are installed already, if not, install automatically:
new.packages <- list.of.packages[!(list.of.packages %in% installed.packages()[,"Package"])]
if(length(new.packages)) install.packages(new.packages, repos = "http://cran.us.r-project.org")
#Load packages
lapply(list.of.packages, require, character.only = TRUE)



#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~DATA SETUP~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
the_data <- read_tsv(args)

exploratory_data <- the_data %>% select(-starts_with("denominator"))

data4pca <- the_data %>% select(-starts_with("median")) %>% select(-starts_with("denominator")) %>% spread (marker, EMD_no_norm_arc) %>% column_to_rownames(., var = "file_origin")#read_tsv(args)
#Calculate row SD for later use in PCA plots
calculated_sd <- rowSds(as.matrix.data.frame(data4pca))

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#


###############################################################################
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#~UI~#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
###############################################################################
ui <- bootstrapPage(
    mainPanel(
    titlePanel("EMD: iPCA"),
        
        tabsetPanel(
            tabPanel("Inspect the data",

                p("Here is the data from the input file after removing unnecessary columns and collapsing marker EMD scores for each condition:"),
                DT::dataTableOutput('contents'),
                # tags$hr(),
                # p("The tableplot below (it will take a few seconds to appear) may be useful to explore the relationships between the variables, to discover strange data patterns, and to check the occurrence and selectivity of missing values."),
                # plotOutput("tableplot")
        ), # end  tab
            tabPanel("Correlation Plots",
                sidebarLayout(
                    sidebarPanel(
                        uiOutput("choose_columns_biplot")
                    ),
                    mainPanel(
                        h2("Correlation plot"),
                        p("This plot may take a few moments to appear when analysing large datasets. You may want to exclude highly correlated variables from the PCA."),
                        plotOutput("corr_plot"),
                        downloadButton('dwn_corr', "Download plot as .pdf")
                    )
                ),
                tags$hr(),
                p("Summary of correlations"),
                tableOutput("corr_tables")
        ), # end  tab
            tabPanel("Diagnostics",
                h2("KMO test"),
                p("Here is the output of the Kaiser-Meyer-Olkin (KMO) index test. The overall measure varies between 0 and 1, and values closer to 1 are better. A value of 0.6 is a suggested minimum. "),
                p("This test provides some guidelines on the suitability of the data for a principal components analysis. However, it may be safely ignored in favour of common sense such as when working with very few conditions and markers (such as when studying cell types and the EMD scores for just the PTMs). Variables with zero variance are excluded."),
                verbatimTextOutput("kmo")
        ), # end  tab
            tabPanel("Compute PCA",
                p("Only columns containing numeric data are shown here because PCA doesn't work with non-numeric data and variables with zero variance have been automatically removed because they're not useful in a PCA."),
                p("The PCA is automatically re-computed each time you change your selection."),
                tags$hr(),
                sidebarLayout(
                    sidebarPanel(
                        p("Choose the columns of your data to include in the PCA."),
                        uiOutput("choose_columns_pca")
                    ),
                    mainPanel(
                        p("Select options for the PCA computation (we are using the prcomp function here)"),
                        radioButtons(inputId = 'center',  
                                    label = 'Center',
                                    choices = c('Shift variables to be zero centered'='Yes',
                                                'Do not shift variables'='No'), 
                                    selected = 'Yes'),
                        radioButtons('scale.', 'Scale',
                                    choices = c('Scale variables to have unit variance'='Yes',
                                                'Do not scale variables'='No'), 
                                    selected = 'Yes')
                    )
                )
        ), # end  tab
            tabPanel("PC Plots",
                h2("Scree plot"),
                p("The scree plot shows the variances of each PC, and the cumulative variance explained by each PC (in %) "),
                plotOutput("plot2", height = "300px"),
                tags$hr(),
                h2("PC plot: zoom and select points"),
                # p("Select the grouping variable."),
                # p("Only variables where the number of unique values is less than 10% of the total number of observations are shown here (because seeing groups with 1-2 observations is usually not very useful)."),
                # uiOutput("the_grouping_variable"),
                # tags$hr(),
                p("Select the PCs to plot"),
                uiOutput("the_pcs_to_plot_x"),
                uiOutput("the_pcs_to_plot_y"),
                tags$hr(),
                
                p("Click and drag on the first plot below to zoom into a region on the plot. Or you can go directly to the second plot below to select points to get more information about them."),
                p("Then select points on zoomed plot below to get more information about the points."),
                p("You can click on the 'Compute PCA' tab at any time to change the variables included in the PCA, and then come back to this tab and the plots will automatically update."),
                plotOutput ("z_plot1",
                            brush = brushOpts(
                            id = "z_plot1Brush",
                            resetOnNew = TRUE)),
                tags$hr(),
                sidebarLayout(
                    sidebarPanel(
                        p("Click and drag on the plot below to select points, and inspect the table of selected points below"),
                        plotOutput("z_plot2",
                                   brush = brushOpts(
                                       id = "plot_brush_after_zoom",
                                       resetOnNew = TRUE)),
                        downloadButton('dwn_pcaplot', "Download plot as .pdf")
                    ),
                    mainPanel(
                        p("Interactive PCA plot from Plotly. Useful for inspecting coordinates and SD values"),
                        plotlyOutput ("plotly_pca")
                    )
                )
        ), # end  tab 
            tabPanel("PCA output",
                downloadButton("dwn_pcainfo", "Download pca information"),
                # downloadButton("dwn_pcasummary", "Download pca summary information"),     
                verbatimTextOutput("pca_details")
        )#, # end  tab 
            # tabPanel("Authorship",
            #     p("The code for this Shiny app is online at ", a("https://github.com/benmarwick/Interactive_PCA_Explorer", href = "https://github.com/benmarwick/Interactive_PCA_Explorer"), "Based on the original work of ", a("Ben Marwick", href = "https://github.com/benmarwick"),".")
        #)
        ) 

    )
)


###############################################################################
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#~Server~#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
###############################################################################

server <- function(input, output, session) {
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~Inspect the data~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
    # tableplot
    output$tableplot <- renderPlot({
        tabplot::tableplot(exploratory_data)
    })
    # display a table of the CSV contents
    output$contents <-  DT::renderDataTable({
        data4pca
    })

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~Correlation plots~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~# 
    # Check boxes to choose columns
    output$choose_columns_biplot <- renderUI({
        colnames <- names(data4pca)
        # Create the checkboxes and select them all by default
        checkboxGroupInput("columns_biplot", "Choose up to five columns to display on the scatterplot matrix", 
                            choices  = colnames,
                            selected = colnames[1:5])
    })
    # corr plot
    output$corr_plot <- renderPlot({
        # Keep the selected columns
        columns_biplot <-    input$columns_biplot
        the_data_subset_biplot <- data4pca[, columns_biplot, drop = FALSE]
        ggpairs(the_data_subset_biplot)
    })
    # corr tables
    output$corr_tables <- renderTable({
        # we only want to show numeric cols
        the_data_num <- data4pca[,sapply(data4pca,is.numeric)]
        # exclude cols with zero variance
        the_data_num <- the_data_num[,!apply(the_data_num, MARGIN = 2,
                        function(x) max(x, na.rm = TRUE) == min(x, na.rm = TRUE))]
        res <- Hmisc::rcorr(as.matrix(the_data_num))
        cormat <- res$r
        pmat <- res$P
        ut <- upper.tri(cormat)
        df <- data.frame(
            row = rownames(cormat)[row(cormat)[ut]],
            column = rownames(cormat)[col(cormat)[ut]],
            cor  = (cormat)[ut],
            p = pmat[ut])
        with(df, df[order(-cor), ])
    })
    output$dwn_corr <- downloadHandler(
        filename <- "correlation_plot.pdf",
        content = function(file) {
            ggsave(file, plot = ggpairs(data4pca[, input$columns_biplot, drop=FALSE]), device="pdf")
        }
    )
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~Diagnostics~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
    #KMO test
    output$kmo <- renderPrint({
        the_data_num <- data4pca[,sapply(data4pca,is.numeric)]
        # exclude cols with zero variance
        the_data_num <- the_data_num[,!apply(the_data_num, MARGIN = 2, function(x) max(x, na.rm = TRUE) == min(x, na.rm = TRUE))]

        # http://www.opensubscriber.com/message/r-help@stat.math.ethz.ch/7315408.html
        # KMO Kaiser-Meyer-Olkin Measure of Sampling Adequacy 
        kmo = function( data ){ 

            library(MASS) 
            X <- cor(as.matrix(data)) 
            iX <- ginv(X) 
            S2 <- diag(diag((iX^-1))) 
            AIS <- S2%*%iX%*%S2                      # anti-image covariance matrix 
            IS <- X+AIS-2*S2                         # image covariance matrix 
            Dai <- sqrt(diag(diag(AIS))) 
            IR <- ginv(Dai)%*%IS%*%ginv(Dai)         # image correlation matrix 
            AIR <- ginv(Dai)%*%AIS%*%ginv(Dai)       # anti-image correlation matrix 
            a <- apply((AIR - diag(diag(AIR)))^2, 2, sum) 
            AA <- sum(a) 
            b <- apply((X - diag(nrow(X)))^2, 2, sum) 
            BB <- sum(b) 
            MSA <- b/(b+a)                        # indiv. measures of sampling adequacy 
            
            AIR <- AIR-diag(nrow(AIR))+diag(MSA)  # Examine the anti-image of the 
            # correlation matrix. That is the 
            # negative of the partial correlations, 
            # partialling out all other variables. 
            
            kmo <- BB/(AA+BB)                     # overall KMO statistic 
            # Reporting the conclusion 
            if (kmo >= 0.00 && kmo < 0.50){ 
                test <- 'The KMO test yields a degree of common variance 
                unacceptable for FA.' 
            } else if (kmo >= 0.50 && kmo < 0.60){ 
                test <- 'The KMO test yields a degree of common variance miserable.' 
            } else if (kmo >= 0.60 && kmo < 0.70){ 
                test <- 'The KMO test yields a degree of common variance mediocre.' 
            } else if (kmo >= 0.70 && kmo < 0.80){ 
                test <- 'The KMO test yields a degree of common variance middling.' 
            } else if (kmo >= 0.80 && kmo < 0.90){ 
                test <- 'The KMO test yields a degree of common variance meritorious.' 
            } else { 
                test <- 'The KMO test yields a degree of common variance marvelous.' 
            } 
            ans <- list(  overall = kmo, 
                            report = test, 
                            individual = MSA, 
                            AIS = AIS, 
                            AIR = AIR ) 
            return(ans) 
            }    # end of kmo() 
        kmo(na.omit(the_data_num))
    }) 

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~Compute PCA~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~# 
    # Check boxes to choose columns
    output$choose_columns_pca <- renderUI({
        # we only want to show numeric cols
        the_data_num <- na.omit(data4pca[,sapply(data4pca,is.numeric)])
        # exclude cols with zero variance
        the_data_num <- the_data_num[,!apply(the_data_num, MARGIN = 2, function(x) max(x, na.rm = TRUE) == min(x, na.rm = TRUE))]
        colnames <- names(the_data_num)
        # Create the checkboxes and select them all by default
        checkboxGroupInput("columns", "Choose columns", 
                            choices  = colnames,
                            selected = colnames)
    })
    # # choose a grouping variable
    # output$the_grouping_variable <- renderUI({
    #     # for grouping we want to see only cols where the number of unique values are less than 
    #     # 10% the number of observations
    #     grouping_cols <- sapply(seq(1, ncol(data4pca)), function(i) length(unique(data4pca[,i])) < nrow(data4pca)/10 )
    #     the_data_group_cols <- data4pca[, grouping_cols, drop = FALSE]
    #     # drop down selection
    #     selectInput(inputId = "the_grouping_variable", 
    #                 label = "Grouping variable:",
    #                 choices=c("None", names(the_data_group_cols)))
    # })
    pca_objects <- reactive({
        # Keep the selected columns
        columns <-    input$columns
        the_data <- na.omit(data4pca)
        the_data_subset <- na.omit(the_data[, columns, drop = FALSE])
        # from http://rpubs.com/sinhrks/plot_pca
        pca_output <- prcomp(na.omit(the_data_subset), 
                        center = (input$center == 'Yes'), 
                        scale. = (input$scale. == 'Yes'))
        # data.frame of PCs
        pcs_df <- cbind(the_data, pca_output$x)
            return(list(the_data = the_data, 
                the_data_subset = the_data_subset,
                pca_output = pca_output, 
                pcs_df = pcs_df))
    })

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~PCA plots~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
    output$the_pcs_to_plot_x <- renderUI({
        pca_output <- pca_objects()$pca_output$x
        # drop down selection
        selectInput(inputId = "the_pcs_to_plot_x", 
                    label = "X axis:",
                    choices= colnames(pca_output), 
                    selected = 'PC1')
    })
    output$the_pcs_to_plot_y <- renderUI({
        pca_output <- pca_objects()$pca_output$x
        # drop down selection
        selectInput(inputId = "the_pcs_to_plot_y", 
                    label = "Y axis:",
                    choices= colnames(pca_output), 
                    selected = 'PC2')
    })
    output$plot2 <- renderPlot({
        pca_output <- pca_objects()$pca_output
        fviz_eig(pca_output, addlabels = TRUE)
    })
    # PC plot
    pca_biplot <- reactive({
        pcs_df <- pca_objects()$pcs_df
        pca_output <-  pca_objects()$pca_output
        var_expl_x <- round(100 * pca_output$sdev[as.numeric(gsub("[^0-9]", "", 
                        input$the_pcs_to_plot_x))]^2/sum(pca_output$sdev^2), 1)
        var_expl_y <- round(100 * pca_output$sdev[as.numeric(gsub("[^0-9]", "", 
                        input$the_pcs_to_plot_y))]^2/sum(pca_output$sdev^2), 1)
        labels <- rownames(pca_output$x)
        eixos = c(1,2)
        eixos = c(substr(input$the_pcs_to_plot_x, nchar(input$the_pcs_to_plot_x), 
                nchar(input$the_pcs_to_plot_x)), substr(input$the_pcs_to_plot_y, 
                nchar(input$the_pcs_to_plot_y), nchar(input$the_pcs_to_plot_y)))
        
        fviz_pca_biplot(pca_output,
            axes = as.numeric(eixos),
            col.ind = rownames(data4pca),
            alpha.var="contrib" ) + 
            geom_point(aes(color = rownames(data4pca),size=(calculated_sd))) +
            guides(alpha="none", shape="none", size=guide_legend(title = "SD"))
        
    })
    # for zooming
    output$z_plot1 <- renderPlot({
        pca_biplot()
    })
    
    output$plotly_pca <- renderPlotly({
        pcs_df <- pca_objects()$pcs_df
        pca_output <-  pca_objects()$pca_output
        var_expl_x <- round(100 * pca_output$sdev[as.numeric(gsub("[^0-9]", "", 
                                                                  input$the_pcs_to_plot_x))]^2/sum(pca_output$sdev^2), 1)
        var_expl_y <- round(100 * pca_output$sdev[as.numeric(gsub("[^0-9]", "", 
                                                                  input$the_pcs_to_plot_y))]^2/sum(pca_output$sdev^2), 1)
        labels <- rownames(pca_output$x)
        eixos = c(1,2)
        eixos = c(substr(input$the_pcs_to_plot_x, nchar(input$the_pcs_to_plot_x), 
                         nchar(input$the_pcs_to_plot_x)), substr(input$the_pcs_to_plot_y, 
                         nchar(input$the_pcs_to_plot_y), nchar(input$the_pcs_to_plot_y)))
        
        print (ggplotly(fviz_pca_biplot(pca_output,
                                 axes = as.numeric(eixos)) + 
                     geom_point(aes(color = rownames(data4pca),size=(calculated_sd))) +
                     guides(shape="none", size=guide_legend(title = "SD"))))
    })
    
    # zoom ranges
    zooming <- reactiveValues(x = NULL, y = NULL)
    observe({
        brush <- input$z_plot1Brush
        if (!is.null(brush)) {
            zooming$x <- c(brush$xmin, brush$xmax)
            zooming$y <- c(brush$ymin, brush$ymax)
        }
        else {
            zooming$x <- NULL
            zooming$y <- NULL
        }
    })
    # for zooming
    output$z_plot2 <- renderPlot({
        pca_biplot() + coord_cartesian(xlim = zooming$x, ylim = zooming$y) 
    })
    output$dwn_pcaplot <- downloadHandler(
        filename <- "pca_plot.pdf",
        content = function(file) {
            ggsave(file, plot = pca_biplot() + coord_cartesian(xlim = zooming$x, ylim = zooming$y), height=12, width=20, device="pdf")
        }
    )
    

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~PCA output~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#    
    output$pca_details <- renderPrint({
        print(get_pca_ind(pca_objects()$pca_output)$coord)
    })
    output$dwn_pcainfo <- downloadHandler(
        filename = "pca_info.txt",
        content = function(file) {
            write.table(get_pca_ind(pca_objects()$pca_output)$coord, file, sep = "\t",
            row.names = TRUE, col.names = NA)
        }
    )
    # output$dwn_pcasummary <- downloadHandler(
    #     filename = "pca_summary.txt",
    #     sum_info <- summary(pca_objects()$pca_output),
    #     content = function(file) {
    #         print(class(sum_info))
    #         write.table(sum_info, file, sep = "\t",
    #         row.names = TRUE, col.names = NA)
    #     }
    # )
    #session$onSessionEnded(stopApp)
}


###############################################################################
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#~Run PCA~#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
###############################################################################
# Run the application 
shinyApp(ui = ui, server = server)