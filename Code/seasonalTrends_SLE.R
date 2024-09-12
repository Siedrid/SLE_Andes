# Seasonal Trends and Anomalies of SLE

library(dplyr)
library(ggplot2)
library(Kendall)
library(trend)

sens.slope(JFM_med$median_RSLE)
plot_mk <- function(ts, month_str) {
  # Perform the Mann-Kendall test
  result <- MannKendall(ts$median_RSLE)
  print(result)
  
  # Calculate the trend line
  sen <- sens.slope(ts$median_RSLE)
  slope <- sen$estimates %>% unname()
  intercept <- mean(ts$median_RSLE) - slope * mean(ts$year)
  trend_line <- slope * ts$year + intercept

  # Create the plot
  p <- ggplot(ts, aes(x = year, y = median_RSLE)) +
    geom_line(color = "blue", size = 1) +
    geom_point(color = "blue") +
    geom_line(aes(y = trend_line), color = "red", linetype = "dashed") +
    labs(title = month_str, y = "Median SLE [m]", x = "Year") +
    annotate("text", x = ts$year[3], y = max(ts$median_RSLE) - 200, 
             label = paste("Trend: ", round(slope,2), " m/year"), size = 4) +
    annotate("text", x = ts$year[3], y = max(ts$median_RSLE) - 400, 
             label = paste("p-value: ", round(result$sl[1], 4)), size = 4) +
    theme_minimal()
  
  return(p)
}

filtered <- read.csv("D:/SLE_Anden/SLE/00001_Aconcaqua/00001_Aconcaguaraw_filtered.csv")


# Define the months for JFM, ON, and JJA
JFM <- c(1, 2, 3)
ON <- c(10, 11)
JJA <- c(6, 7, 8)

# Calculate median and mean for RSLE in JFM
JFM_df <- filtered %>% filter(month %in% JFM)
JFM_med <- JFM_df %>% group_by(year) %>% summarize(median_RSLE = median(RSLE, na.rm = TRUE))
JFM_mean <- JFM_df %>% group_by(year) %>% summarize(mean_RSLE = mean(RSLE, na.rm = TRUE))

# Filter data for ON
ON_df <- filtered %>% filter(month %in% ON)

# Calculate median and mean for RSLE in ON
ON_med <- ON_df %>% group_by(year) %>% summarize(median_RSLE = median(RSLE, na.rm = TRUE))
ON_mean <- ON_df %>% group_by(year) %>% summarize(mean_RSLE = mean(RSLE, na.rm = TRUE))

# Filter data for JJA
JJA_df <- filtered %>% filter(month %in% JJA)

# Calculate median and mean for RSLE in JJA
JJA_med <- JJA_df %>% group_by(year) %>% summarize(median_RSLE = median(RSLE, na.rm = TRUE))
JJA_mean <- JJA_df %>% group_by(year) %>% summarize(mean_RSLE = mean(RSLE, na.rm = TRUE))

# Create the plots for JFM, JJA, and ON
p1 <- plot_mk(JFM_med, "JFM")
p2 <- plot_mk(JJA_med, "JJA")
p3 <- plot_mk(ON_med, "ON")

# Arrange the plots in a single output (equivalent to plt.subplots)
library(gridExtra)
grid.arrange(p1, p2, p3, nrow = 3)


# Combine the plots
# Load necessary libraries
library(ggplot2)
library(trend)

# Create a function to combine anomalies and trend line with a secondary y-axis
plot_combined <- function(ts, month_str) {
  
  # Calculate the long-term median for anomalies (1990-2020 period)
  sle_train <- ts[ts$year >= 1990 & ts$year <= 2020,]
  lt_med <- median(sle_train$median_RSLE)
  
  # Calculate the anomalies (SLE - long-term median)
  ts$anomalies <- ts$median_RSLE - lt_med
  
  # Perform the Mann-Kendall test and calculate Sen's slope
  mk_result <- MannKendall(ts$median_RSLE)
  sen_result <- sens.slope(ts$median_RSLE)
  slope <- sen_result$estimates
  
  # Calculate the intercept for the trend line
  intercept <- mean(ts$median_RSLE) - slope * mean(ts$year)
  ts$trend_line <- slope * ts$year + intercept
  
  # Create the plot with a secondary y-axis for anomalies
  p <- ggplot(ts, aes(x = year)) +
    
    # Snow line data (median SLE values on the left axis)
    geom_line(aes(y = median_RSLE), color = "blue", size = 1) +
    
    # Trend line (also on the left axis)
    geom_line(aes(y = trend_line), color = "red", linetype = "dashed", size = 1) +
    
    # Anomaly bars (plotted on a scaled secondary y-axis)
    geom_bar(aes(y = anomalies), stat = "identity", fill = "lightblue", alpha = 0.5) +  # Scaling down anomalies
    
    # Title and labels
    labs(title = month_str, x = "Year", y = "Median SLE [m]") +
    
    # Secondary y-axis for anomalies (without scaling)
    scale_y_continuous(
      name = "Median SLE [m]",
      sec.axis = sec_axis(~ . *0.1, name = "SLE Anomalies [m]")  # Scale the secondary axis back to match the original anomaly values
    ) +
    
    # Annotations for slope and p-value
    annotate("text", x = ts$year[2], y = max(ts$median_RSLE) - 200,
             label = paste("Trend: ", round(slope, 2), " m/year"), size = 4) +
    annotate("text", x = ts$year[2], y = max(ts$median_RSLE) - 400,
             label = paste("p-value: ", round(mk_result$sl[1], 4)), size = 4) +
    
    # Minimal theme
    theme_minimal() +
    
    # Adjust theme to color the right y-axis
    theme(
      axis.title.y.right = element_text(color = "lightblue"),  # Color the secondary axis label
      axis.text.y.right = element_text(color = "lightblue")    # Color the secondary axis tick labels
    )
  
  return(p)
}

# Example usage
# Assuming JFM_med, JJA_med, and ON_med are data frames with 'year' and 'median_RSLE' columns
plot_combined(JFM_med, "JFM")
p2 <- plot_combined(JJA_med, "JJA")
p3 <- plot_combined(ON_med, "ON")

# Display all plots together
library(gridExtra)
grid.arrange(p1, p2, p3, nrow = 3)
