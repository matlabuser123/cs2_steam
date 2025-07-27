.PHONY: install_drivers verify_drivers run_perftest dashboard docker all clean clean_logs log test help

install_drivers:
	@if conda info --envs | grep -q "cs2_optimizer"; then \
		echo "Installing drivers..."; \
		conda run -n cs2_optimizer python main.py --install-drivers || echo "Driver installation failed. Check logs for details."; \
	else \
		echo "Conda environment 'cs2_optimizer' not found. Please create it using:"; \
		echo "  conda create -n cs2_optimizer python=3.11 -y"; \
		echo "  conda activate cs2_optimizer"; \
		echo "  pip install -r requirements.txt"; \
	fi

verify_drivers:
	@if conda info --envs | grep -q "cs2_optimizer"; then \
		echo "Verifying drivers..."; \
		conda run -n cs2_optimizer python main.py --verify-drivers || echo "Driver verification failed. Check logs for details."; \
	else \
		echo "Conda environment 'cs2_optimizer' not found. Please create it."; \
	fi

run_perftest:
	@if conda info --envs | grep -q "cs2_optimizer"; then \
		echo "Running performance tests..."; \
		conda run -n cs2_optimizer python main.py --run-perftest || echo "Performance test failed. Check logs for details."; \
	else \
		echo "Conda environment 'cs2_optimizer' not found. Please create it."; \
	fi

dashboard:
	@if conda info --envs | grep -q "cs2_optimizer"; then \
		echo "Launching Streamlit dashboard..."; \
		conda run -n cs2_optimizer streamlit run dashboard.py --server.port 8501 --server.enableCORS false || echo "Failed to launch dashboard."; \
	else \
		echo "Conda environment 'cs2_optimizer' not found. Please create it."; \
	fi

docker:
	@echo "Building and running Docker containers..."
	@docker-compose up --build || echo "Docker operation failed. Check logs for details."

test:
	@if conda info --envs | grep -q "cs2_optimizer"; then \
		echo "Running tests..."; \
		conda run -n cs2_optimizer pytest || echo "Tests failed. Check logs for details."; \
	else \
		echo "Conda environment 'cs2_optimizer' not found. Please create it."; \
	fi

all: install_drivers verify_drivers run_perftest

clean:
	@echo "Cleaning up extracted driver folders..."
	@rm -rf msi_drivers/*_extracted
	@echo "Cleaned up extracted driver folders."

clean_logs:
	@echo "Cleaning up log files..."
	@rm -f *.log
	@echo "Log files cleaned."

log:
	@echo "Displaying driver installation log..."
	@cat driver_install.log || echo "Log file not found."

help:
	@echo "Available targets:"
	@echo "  install_drivers   - Install all drivers."
	@echo "  verify_drivers    - Verify installed drivers."
	@echo "  run_perftest      - Run performance tests."
	@echo "  dashboard         - Launch the Streamlit dashboard."
	@echo "  docker            - Build and run Docker containers."
	@echo "  test              - Run tests using pytest."
	@echo "  all               - Run install_drivers, verify_drivers, and run_perftest."
	@echo "  clean             - Clean up extracted driver folders."
	@echo "  clean_logs        - Clean up log files."
	@echo "  log               - Display the driver installation log."
	@echo "  help              - Display this help message."
