# R version of the Python analysis (same data, same results).
# Usage (from the repository root):  Rscript analysis/R/paralel_analysis.R
# Needs: install.packages("ggplot2")

suppressPackageStartupMessages(library(ggplot2))

xs <- read.csv("data/cross_sections.csv", stringsAsFactors = FALSE)
dir.create("figures/r", showWarnings = FALSE, recursive = TRUE)

# ---- checks: every section adds up to 40 m ----
totals <- tapply(xs$width_m, xs$section, sum)
stopifnot(all(abs(totals - 40) < 0.05))

# ---- indicators ----
modes  <- c("walk", "bike", "buffer", "traffic", "parking", "median")
labels <- c(walk = "Walking", bike = "Cycling", buffer = "Buffer", traffic = "Traffic lanes",
            parking = "Parking / loading", median = "Median / divider")
typical <- subset(xs, section %in% c("before", "after"))
share <- aggregate(width_m ~ section + mode, data = typical, FUN = sum)
share <- merge(expand.grid(section = c("before", "after"), mode = modes, stringsAsFactors = FALSE),
               share, all.x = TRUE)
share$width_m[is.na(share$width_m)] <- 0
share$pct <- 100 * share$width_m / 40

bike_before <- subset(xs, section == "before" & mode == "bike")$width_m / 2   # two-way lane
bike_after  <- min(subset(xs, section == "after" & mode == "bike")$width_m)  # one-way tracks
cat(sprintf("Cycling width per direction: %.2f m -> %.2f m (%+.0f%%)\n",
            bike_before, bike_after, 100 * (bike_after - bike_before) / bike_before))
print(reshape(share[, c("section", "mode", "pct")], idvar = "mode", timevar = "section", direction = "wide"),
      row.names = FALSE, digits = 3)

# ---- figure 1: space allocation before vs after ----
share$mode <- factor(share$mode, levels = rev(modes), labels = rev(labels[modes]))
share$section <- factor(share$section, levels = c("after", "before"), labels = c("After", "Before"))
p1 <- ggplot(share, aes(x = pct, y = mode, fill = section)) +
  geom_col(position = position_dodge(width = 0.8), width = 0.72) +
  geom_text(aes(label = sprintf("%.1f%%", pct)), position = position_dodge(width = 0.8),
            hjust = -0.15, size = 2.8, colour = "#3d3d3a") +
  scale_fill_manual(values = c(Before = "#2a78d6", After = "#eb6834"), breaks = c("Before", "After")) +
  scale_x_continuous(limits = c(0, 46), expand = c(0, 0)) +
  labs(title = "Space allocation on Av. del Paral\u00b7lel, before and after",
       x = "Share of the 40 m street (%)", y = NULL, fill = NULL) +
  theme_minimal(base_size = 10) +
  theme(panel.grid.major.y = element_blank(), panel.grid.minor = element_blank(),
        legend.position = "bottom", plot.title = element_text(size = 11))
ggsave("figures/r/space_allocation.png", p1, width = 8, height = 4.2, dpi = 200, bg = "white")

# ---- figure 2: CROW width check over cyclist volumes ----
crow_one_way <- function(v) ifelse(v <= 150, 2.0, ifelse(v <= 750, 2.5, 3.5))
crow_two_way <- function(v) ifelse(v <= 150, 2.5, ifelse(v <= 350, 3.5, 4.5))
vols <- 0:800
crow <- rbind(data.frame(volume = vols, width = crow_one_way(vols), type = "CROW minimum, one-way track"),
              data.frame(volume = vols, width = crow_two_way(vols), type = "CROW minimum, two-way path"))
p2 <- ggplot(crow, aes(volume, width, colour = type)) +
  geom_step(linewidth = 1) +
  geom_hline(yintercept = 2.0, linetype = "dotted", colour = "#eb6834") +
  geom_hline(yintercept = 2.2, linetype = "dotted", colour = "#2a78d6") +
  annotate("text", x = 790, y = c(1.88, 2.32), label = c("proposed track 2.0 m", "existing lane 2.2 m"),
           hjust = 1, size = 2.8, colour = "#3d3d3a") +
  scale_colour_manual(values = c("#eb6834", "#2a78d6")) +
  coord_cartesian(ylim = c(0, 5)) +
  labs(title = "Existing lane fails at any volume; proposed track holds up to 150 bikes/h",
       x = "Peak-hour cyclist volume (bikes/h)", y = "Width (m)", colour = NULL) +
  theme_minimal(base_size = 10) +
  theme(legend.position = "top", panel.grid.minor = element_blank(), plot.title = element_text(size = 11))
ggsave("figures/r/crow_width_check.png", p2, width = 8, height = 4, dpi = 200, bg = "white")

# ---- figure 3: scaled cross-sections ----
cols <- c(walk = "#d9d6cc", bike = "#d9534f", buffer = "#f2f1ec", parking = "#9fa6b2",
          traffic = "#5f6670", median = "#7fb069", platform = "#c9b27c")
xs <- xs[order(xs$section, xs$order), ]
xs$x1 <- ave(xs$width_m, xs$section, FUN = cumsum)
xs$x0 <- xs$x1 - xs$width_m
xs$section <- factor(xs$section, levels = c("before", "after", "after_bus_stop"),
                     labels = c("Existing section", "Proposed section (typical)", "Proposed section at a bus stop"))
xs$lab <- ifelse(xs$width_m >= 0.5, sprintf("%s\n%.1f m", sub(" \\(.*", "", xs$element), xs$width_m), "")
p3 <- ggplot(xs) +
  geom_rect(aes(xmin = x0 + 0.04, xmax = x1 - 0.04, ymin = 0, ymax = 1, fill = mode)) +
  geom_text(aes(x = (x0 + x1) / 2, y = 0.5, label = lab, angle = ifelse(width_m < 3.2, 90, 0)),
            size = 1.9, colour = ifelse(xs$mode %in% c("traffic", "bike", "median", "parking"), "white", "#1f1f1e")) +
  scale_fill_manual(values = cols, guide = "none") +
  facet_wrap(~section, ncol = 1) +
  labs(x = "Distance from the north building line (m)", y = NULL) +
  theme_minimal(base_size = 9) +
  theme(axis.text.y = element_blank(), panel.grid = element_blank())
ggsave("figures/r/cross_sections.png", p3, width = 11, height = 6, dpi = 200, bg = "white")
cat("Figures written to figures/r/\n")
