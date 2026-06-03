# ─────────────────────────────────────────────────────────
# Dockerfile
# ─────────────────────────────────────────────────────────
# Runs the pick-and-place demo inside a ROS 2 Humble container.
#
# Build:
#   docker build -t pick-place-demo .
#
# Run (standalone demo):
#   docker run --rm pick-place-demo
#
# Run (custom bin/place zones):
#   docker run --rm pick-place-demo python main.py --bin B2 --place P2
#
# Run (with ROS 2 environment sourced):
#   docker run --rm --network host pick-place-demo \
#       bash -c "source /opt/ros/humble/setup.bash && python main.py"
# ─────────────────────────────────────────────────────────

# Base image: ROS 2 Humble on Ubuntu 22.04 (standard for industrial robotics)
FROM ros:humble-ros-base

# Set working directory inside the container
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the full project into the container
COPY . .

# Default command: run the standalone demo
CMD ["python", "main.py"]
