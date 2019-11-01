args <- commandArgs(trailingOnly = TRUE)

#Packages to use:
list.of.packages <- c("ggplot2", 
                        "DT", 
                        "GGally",
                        "psych",
                        "Hmisc",
                        "MASS",
                        "tabplot",
                        "readr",
                        "dplyr",
                        "forcats",
                        "RColorBrewer",
                        "shiny")
# check if pkgs are installed already, if not, install automatically:
new.packages <- list.of.packages[!(list.of.packages %in% installed.packages()[,"Package"])]
if(length(new.packages)) install.packages(new.packages, repos = "http://cran.us.r-project.org")

#Load packages
lapply(list.of.packages, require, character.only = TRUE)

the_data <- read_tsv(args)

ui <- bootstrapPage(
    mainPanel(
    titlePanel("Interactive PCA Explorer"),
        
        tabsetPanel(
        
        #   tabPanel("Data input", 
        #            p("Before uploading your data, check that it is clean, especially ensure that the the numeric variables contain only the digits 0-9 or NA (to indicate missing data)."),
        #            p("Rows that contain one or more NAs will be excluded from the PCA."),
        #            p("Columns that contain a mixture of numbers and text will not be included in the computation of the PCA results."),
        #            p("Have a look at the ", a("iris.csv", href = "https://raw.githubusercontent.com/benmarwick/Interactive_PCA_Explorer/master/iris.csv"),  " file included with this app to see what a clean CSV file looks like."),
        #            tags$hr(),
        #            p("Select the options that match your CSV file, then upload your file:"),
            
                
        #            radioButtons(inputId = 'header',  
        #                         label = 'Header',
        #                         choices = c('Columns have headers'='Yes',
        #                                     'Columns do not have headers'='No'), 
        #                         selected = 'Yes'),
          
        #            radioButtons('sep', 'Separator',
        #                         c(Comma=',',
        #                           Semicolon=';',
        #                           Tab='\t'),
        #                         ','),
          
        #            radioButtons('quote', 'Quote',
        #                         c(None='',
        #                           'Double Quote'='"',
        #                           'Single Quote'="'"),
        #                         '"'),
                   
        #            tags$hr(),
                   
        #            fileInput('file1', 'Choose a CSV file to upload:',
        #                      accept = c(
        #                        'text/csv',
        #                        'text/comma-separated-values',
        #                        'text/tab-separated-values',
        #                        'text/plain',
        #                        '.csv',
        #                        '.tsv'
        #                      )),
        #            p("After uploading your CSV file, click on the 'Inspect the data' tab"),
        #            tags$hr(),
        #            p("Made by the TAPE LAB, based on the original work of a("Ben Marwick", href = "https://github.com/benmarwick")")
                   
        # ), # end file  tab
            tabPanel("Inspect the data",

                p("The tableplot below (it will take a few seconds to appear) may be useful to explore the relationships between the variables, to discover strange data patterns, and to check the occurrence and selectivity of missing values."),
                plotOutput("tableplot"),
                tags$hr(),
                p("Here is a summary of the data"),
                tableOutput('summary'),
                tags$hr(),
                p("Here is the raw data from the CSV file"),
                DT::dataTableOutput('contents')
        ), # end  tab
            tabPanel("Correlation Plots",
                
                uiOutput("choose_columns_biplot"),
                tags$hr(),
                p("This plot may take a few moments to appear when analysing large datasets. You may want to exclude highly correlated variables from the PCA."),
                plotOutput("corr_plot"),
                tags$hr(),
                p("Summary of correlations"),
                tableOutput("corr_tables")
        ), # end  tab
            tabPanel("Diagnostics",
                
                p("Among SPSS users, these tests are considered to provide some guidelines on the suitability of the data for a principal components analysis. However, they may be safely ignored in favour of common sense. Variables with zero variance are excluded."),
                tags$hr(),
                p("Here is the output of Bartlett's sphericity test. Bartlett's test of sphericity tests whether the data comes from multivariate normal distribution with zero covariances. If p > 0.05 then PCA may not be very informative"),
                verbatimTextOutput("bartlett"),
                tags$hr(),
                p("Here is the output of the Kaiser-Meyer-Olkin (KMO) index test. The overall measure varies between 0 and 1, and values closer to 1 are better. A value of 0.6 is a suggested minimum. "),
                verbatimTextOutput("kmo")
        ), # end  tab
            tabPanel("Compute PCA",
                
                p("Choose the columns of your data to include in the PCA."),
                p("Only columns containing numeric data are shown here because PCA doesn't work with non-numeric data."),
                p("The PCA is automatically re-computed each time you change your selection."),
                p("Observations (ie. rows) are automatically removed if they contain any missing values."),
                p("Variables with zero variance have been automatically removed because they're not useful in a PCA."),
                uiOutput("choose_columns_pca"),
                tags$hr(),
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
        ), # end  tab
            tabPanel("PC Plots",
                
                h2("Scree plot"),
                p("The scree plot shows the variances of each PC, and the cumulative variance explained by each PC (in %) "),
                plotOutput("plot2", height = "300px"),
                tags$hr(),
                h2("PC plot: zoom and select points"),
                p("Select the grouping variable."),
                p("Only variables where the number of unique values is less than 10% of the total number of observations are shown here (because seeing groups with 1-2 observations is usually not very useful)."),
                uiOutput("the_grouping_variable"),
                tags$hr(),
                p("Select the PCs to plot"),
                uiOutput("the_pcs_to_plot_x"),
                uiOutput("the_pcs_to_plot_y"),
                tags$hr(),
                
                p("Click and drag on the first plot below to zoom into a region on the plot. Or you can go directly to the second plot below to select points to get more information about them."),
                p("Then select points on zoomed plot below to get more information about the points."),
                p("You can click on the 'Compute PCA' tab at any time to change the variables included in the PCA, and then come back to this tab and the plots will automatically update."),
                plotOutput ("z_plot1", height = 400,
                            brush = brushOpts(
                            id = "z_plot1Brush",
                            resetOnNew = TRUE)),
                tags$hr(),
                
                p("Click and drag on the plot below to select points, and inspect the table of selected points below"),
                plotOutput("z_plot2", height = 400,
                            brush = brushOpts(
                            id = "plot_brush_after_zoom",
                            resetOnNew = TRUE)),
                tags$hr(),
                p("Details of the brushed points"),
                tableOutput("brush_info_after_zoom")
        ), # end  tab 
            tabPanel("PCA output",
                
                verbatimTextOutput("pca_details")
        ), # end  tab 
            tabPanel("Authorship",
                
                p("The code for this Shiny app is online at ", a("https://github.com/benmarwick/Interactive_PCA_Explorer", href = "https://github.com/benmarwick/Interactive_PCA_Explorer"), "Based on the original work of ", a("Ben Marwick", href = "https://github.com/benmarwick"),"."))
        ) # end  tab 

    )
)


####
server <- function(input, output, session) {
  
#   # read in the CSV
#   the_data_fn <- reactive({
#     inFile <- input$file1
#     if (is.null(inFile)) return(NULL)
#     the_data <-   read.csv(inFile$datapath, header = (input$header == "Yes"),
#                                sep = input$sep, quote = input$quote, stringsAsFactors=FALSE)
#     return(the_data)
#   })

  
  # tableplot
  output$tableplot <- renderPlot({
    if(is.null(the_data_fn())) return()
    the_data <- the_data_fn()
    tabplot::tableplot(the_data)
    
  })
  
  # display a table of the CSV contents
  output$contents <-  DT::renderDataTable({
    #
    the_data_fn()
  })
  
  # display a summary of the CSV contents
  output$summary <-  renderTable({
    the_data <- the_data_fn()
    psych::describe(the_data)
  })
  
  # Check boxes to choose columns
  output$choose_columns_biplot <- renderUI({
    
    the_data <- the_data_fn()
    
    colnames <- names(the_data)
    
    # Create the checkboxes and select them all by default
    checkboxGroupInput("columns_biplot", "Choose up to five columns to display on the scatterplot matrix", 
                       choices  = colnames,
                       selected = colnames[1:5])
  })
  
  # corr plot
  output$corr_plot <- renderPlot({
    the_data <- the_data_fn()
    # Keep the selected columns
    columns_biplot <-    input$columns_biplot
    the_data_subset_biplot <- the_data[, columns_biplot, drop = FALSE]
    ggpairs(the_data_subset_biplot)
     })
  
  # corr tables
  output$corr_tables <- renderTable({
    the_data <- the_data_fn()
    # we only want to show numeric cols
    the_data_num <- the_data[,sapply(the_data,is.numeric)]
    # exclude cols with zero variance
    the_data_num <- the_data_num[,!apply(the_data_num, MARGIN = 2, function(x) max(x, na.rm = TRUE) == min(x, na.rm = TRUE))]
    
    
      res <- Hmisc::rcorr(as.matrix(the_data_num))
      cormat <- res$r
      pmat <- res$P
      ut <- upper.tri(cormat)
     df <- data.frame(
        row = rownames(cormat)[row(cormat)[ut]],
        column = rownames(cormat)[col(cormat)[ut]],
        cor  = (cormat)[ut],
        p = pmat[ut]
      )
     with(df, df[order(-cor), ])
    
  })
  
output$bartlett <- renderPrint({
  the_data <- the_data_fn()
  the_data_num <- na.omit(the_data[,sapply(the_data,is.numeric)])
  # exclude cols with zero variance
  the_data_num <- the_data_num[,!apply(the_data_num, MARGIN = 2, function(x) max(x, na.rm = TRUE) == min(x, na.rm = TRUE))]

  cortest.bartlett(cor(the_data_num), n = nrow(the_data_num))
})  

output$kmo <- renderPrint({
  the_data <- the_data_fn()
  the_data_num <- the_data[,sapply(the_data,is.numeric)]
  # exclude cols with zero variance
  the_data_num <- the_data_num[,!apply(the_data_num, MARGIN = 2, function(x) max(x, na.rm = TRUE) == min(x, na.rm = TRUE))]
  
 # R <- cor(the_data_num)
 # KMO(R)
  
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
  
 
  
  # Check boxes to choose columns
  output$choose_columns_pca <- renderUI({
    
    the_data <- the_data_fn()
    
    # Get the data set with the appropriate name
    
    # we only want to show numeric cols
    the_data_num <- na.omit(the_data[,sapply(the_data,is.numeric)])
    # exclude cols with zero variance
    the_data_num <- the_data_num[,!apply(the_data_num, MARGIN = 2, function(x) max(x, na.rm = TRUE) == min(x, na.rm = TRUE))]
    
    
    colnames <- names(the_data_num)
    
    # Create the checkboxes and select them all by default
    checkboxGroupInput("columns", "Choose columns", 
                       choices  = colnames,
                       selected = colnames)
  })
  
  # choose a grouping variable
  output$the_grouping_variable <- renderUI({
    the_data <- the_data_fn()

              
  # for grouping we want to see only cols where the number of unique values are less than 
  # 10% the number of observations
    grouping_cols <- sapply(seq(1, ncol(the_data)), function(i) length(unique(the_data[,i])) < nrow(the_data)/10 )
    
    the_data_group_cols <- the_data[, grouping_cols, drop = FALSE]
    # drop down selection
    selectInput(inputId = "the_grouping_variable", 
                label = "Grouping variable:",
                choices=c("None", names(the_data_group_cols)))

  })
  
  
pca_objects <- reactive({
  # Keep the selected columns
  columns <-    input$columns
  the_data <- na.omit(the_data_fn())
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
    eig = (pca_output$sdev)^2
    variance <- eig*100/sum(eig)
    cumvar <- paste(round(cumsum(variance),1), "%")
    eig_df <- data.frame(eig = eig,
                         PCs = colnames(pca_output$x),
                         cumvar =  cumvar)
    ggplot(eig_df, aes(reorder(PCs, -eig), eig)) +
      geom_bar(stat = "identity", fill = "white", colour = "black") +
      geom_text(label = cumvar, size = 4,
                vjust=-0.4) +
      theme_bw(base_size = 14) +
      xlab("PC") +
      ylab("Variances") +
      ylim(0,(max(eig_df$eig) * 1.1))
  })
  
  
  # PC plot
 pca_biplot <- reactive({
    pcs_df <- pca_objects()$pcs_df
    pca_output <-  pca_objects()$pca_output
    
    var_expl_x <- round(100 * pca_output$sdev[as.numeric(gsub("[^0-9]", "", input$the_pcs_to_plot_x))]^2/sum(pca_output$sdev^2), 1)
    var_expl_y <- round(100 * pca_output$sdev[as.numeric(gsub("[^0-9]", "", input$the_pcs_to_plot_y))]^2/sum(pca_output$sdev^2), 1)
    labels <- rownames(pca_output$x)
    grouping <- input$the_grouping_variable

    if(grouping == 'None'){
      # plot without grouping variable
      pc_plot_no_groups  <- ggplot(pcs_df, 
                                   aes_string(input$the_pcs_to_plot_x, 
                                              input$the_pcs_to_plot_y
                                                  )) +
        
        
        geom_text(aes(label = labels),  size = 5) +
        theme_bw(base_size = 14) +
        coord_equal() +
        xlab(paste0(input$the_pcs_to_plot_x, " (", var_expl_x, "% explained variance)")) +
        ylab(paste0(input$the_pcs_to_plot_y, " (", var_expl_y, "% explained variance)")) 
      # the plot
      pc_plot_no_groups
      
      
    } else {
    # plot with grouping variable
      
      pcs_df$fill_ <-  as.character(pcs_df[, grouping, drop = TRUE])
    pc_plot_groups  <- ggplot(pcs_df, aes_string(input$the_pcs_to_plot_x, 
                                          input$the_pcs_to_plot_y, 
                                          fill = 'fill_', 
                                          colour = 'fill_'
                                          )) +
      stat_ellipse(geom = "polygon", alpha = 0.1) +
    
      geom_text(aes(label = labels),  size = 5) +
      theme_bw(base_size = 14) +
      scale_colour_discrete(guide = FALSE) +
      guides(fill = guide_legend(title = "groups")) +
      theme(legend.position="top") +
      coord_equal() +
      xlab(paste0(input$the_pcs_to_plot_x, " (", var_expl_x, "% explained variance)")) +
      ylab(paste0(input$the_pcs_to_plot_y, " (", var_expl_y, "% explained variance)")) 
    # the plot
    pc_plot_groups
    }
    
    
  })
  
  output$brush_info <- renderTable({
    # the brushing function
    brushedPoints(pca_objects()$pcs_df, input$plot_brush)
  })
  

  # for zooming
  output$z_plot1 <- renderPlot({
    
    pca_biplot() 

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
  
  output$brush_info_after_zoom <- renderTable({
    # the brushing function
    brushedPoints(pca_objects()$pcs_df, input$plot_brush_after_zoom)
  })
  
  output$pca_details <- renderPrint({
    # 
    print(pca_objects()$pca_output$rotation)
    summary(pca_objects()$pca_output)
    
  })
  
  output$Colophon <- renderPrint({
    
    
  })
  
    #session$onSessionEnded(stopApp)
}


# Run the application 
shinyApp(ui = ui, server = server)