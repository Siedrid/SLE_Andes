# Rayshader SLE Aconcagua Catchment

library(terra)
library(dplyr)
library(sf)
library(ggplot2)
library(rayshader)

dem <- "D:/SLE_Anden/SLE/00001_Aconcaqua/DEM_Aconcagua.tif"
sle.lt <- "D:/SLE_Anden/SLE/00001_Aconcaqua/SLE_shapes/00001_Aconcaqua_JULY_SLE.geojson"
sle.lt <- st_read(sle.lt)
sle.2021 <- st_read("D:/SLE_Anden/SLE/00001_Aconcaqua/SLE_shapes/00001_Aconcaqua_JULY2021_SLE.geojson")
dem <- rast(dem)

rst_df <- cbind.data.frame(
  crds(dem, na.rm = F),
  values(dem))

w <- ncol(dem)
h <- nrow(dem)

if (st_crs(sle.lt) != st_crs(dem)) {
  sle.line <- st_transform(sle.lt, crs = st_crs(dem))
}

# Extract coordinates from sf object for plotting in ggplot
sle.line_df <- as.data.frame(st_coordinates(sle.lt))

my_plot <- ggplot()+
  geom_raster(data = rst_df, aes(x = x, y=y, fill = DEM_Aconcagua))+
  scale_alpha(range = c(1,0), na.value = 0)+
  scale_x_continuous("Longitude") +
  
  scale_y_continuous("Latitude", expand = c(0,0)) +
  scale_fill_gradientn("Elevation",
                       colours = terrain.colors(10)) + 
  geom_sf(data = sle.lt, color = "blue")+
  geom_sf(data = sle.2021, color = "red")+
  
  # Legend
  guides(
    fill = guide_legend(
      direction = "horizontal",
      keyheight = unit(1.25, units = "mm"),
      keywidth = unit(5, units = "mm"),
      title.position = "top",
      label.position = "bottom",
      nrow = 1,
      byrow = T
    )
  ) +
  
  # theme
  theme_minimal() +
  theme(
    axis.line = element_blank(),
    axis.title.x = element_blank(),
    axis.title.y = element_blank(),
    axis.text.x = element_blank(),
    axis.text.y = element_blank(),
    legend.position = "top",
    legend.title = element_text(size = 7, color = "grey10"),
    legend.text = element_text(size = 5, color = "grey10"),
    panel.grid.minor = element_blank(),
    panel.grid.major = element_line(color = "white", linewidth = 0),
    plot.background = element_rect(fill = "white", color = NA),
    panel.background = element_rect(fill = "white", color = NA),
    legend.background = element_rect(fill = "white", color = NA),
    plot.margin = unit(c(t = 0, r = 0, b = 0, l = 0), "lines")
  ) +
  labs(
    title = "",
    subtitle = "",
    caption = "",
    x = "",
    y = ""
  )

plot_gg(my_plot, shadow_intensity = 0.7, width = w/1000, height = h/1000,
        multicore = TRUE, scale = 100, raytrace = TRUE,
        offset_edges = T,
        windowsize = c(800,800))

rayshader::render_highquality(
  filename = "default.png",
  preview = T,
  width = w * .85,
  height = h * .85,
  parallel = T,
  interactive = F
)

matrix %>%
  sphere_shade(texture = "desert") %>%
  add_water(detect_water(matrix), color = "desert") %>%
  add_shadow(ray_shade(matrix, zscale = 3), 0.5) %>%
  add_shadow(ambient_shade(matrix), 0) %>%
  plot_3d(matrix, zscale = 10, fov = 0, theta = 135, zoom = 0.75, phi = 45, windowsize = c(1000, 800))