"""
AI System for ATE Equipment - Main Application

This Streamlit application provides an interactive interface for analyzing ATE (Automatic Test Equipment)
by allowing users to select equipment from a database, parse equipment specifications, and perform
market research to find pricing and availability information.

Key Features:
- Equipment database with hardcoded test equipment entries
- Interactive equipment selection interface
- AI-powered option parsing and explanation
- Web scraping for market data and pricing
- Comprehensive analysis results display

Dependencies:
- streamlit: Web application framework
- openai: AI/LLM integration for text processing
- pandas: Data manipulation
- Custom modules: parsing, prompting, effective_scraper
"""

import json
import os
import streamlit as st
import pandas as pd
from openai import OpenAI

# Import custom modules for parsing, AI prompting, and web scraping
from parsing import parse_query, split_options_deterministic
from prompting import normalize_options_via_llm
from effective_scraper import scrape_effective_sites

# Application configuration constants
APP_TITLE = "AI System for ATE Equipment"
API_KEY = API_KEY = ""
MODEL_NAME = "gpt-4"  # OpenAI model to use for AI processing
TEMPERATURE = 0.0  # Temperature setting for AI responses (0.0 = deterministic)

# Configure Streamlit page settings (must be called before any other Streamlit commands)
st.set_page_config(page_title=APP_TITLE, page_icon="🧭", layout="wide")


def get_openai_client() -> OpenAI:
	"""
	Initialize and return an OpenAI client instance.
	
	Returns:
		OpenAI: Configured OpenAI client or None if API key is missing
	"""
	if not API_KEY:
		return None
	return OpenAI(api_key=API_KEY)


def render_message(role: str, content: str):
	"""
	Render a chat message in the Streamlit interface.
	
	Args:
		role (str): Message role ("user" or "assistant")
		content (str): Message content to display
	"""
	if role == "user":
		st.chat_message("user").markdown(content)
	else:
		st.chat_message("assistant").markdown(content)


def _get_hardcoded_data():
	"""
	Return hardcoded ATE equipment database for demonstration purposes.
	
	This function provides a sample dataset of test equipment entries including
	quote information, equipment specifications, and available options.
	
	Returns:
		tuple: (header_string, data_lines_list)
			- header_string: Tab-separated column names
			- data_lines_list: List of tab-separated data rows
	"""
	# Define column headers for the equipment database
	header = "quoteid	createddate	contactname	ID	record_id	createddate	QuoteID	eqModel	eqBrand	options"
	
	# Sample equipment data with various test equipment manufacturers and models
	data_lines = [
		"39061	2025-08-19	Alexander Pollak	4531031	122672	NULL	39061	SMA100B	Rohde & Schwarz	B711/B86/B93/B35",
		"39019	2025-08-05	Giampiero	4530979	122599	NULL	39019	N8976B	Agilent HP Keysight	544/B25/EP5/MTU/PC7/SSD/W7X/FSA/NF2/P44/PFR/2FP/1FP/W7",
		"38804	2025-05-22	Guillermo Leon	4514403	122281	NULL	38804	4500C	BOONTON	006",
		"38713	2025-05-02	LYNN HOOVER	4469255	122154	NULL	38713	N5172B	Agilent HP Keysight	099/1EA/403/506/653/655/657/FRQ/UNV/N7631EMBC",
		"38691	2025-04-30	Mustafa Al Shaikhli	4468233	122123	NULL	38691	MS2090A	Anritsu	0031/0090/0104/0199/0714/0883/0888",
		"28871	2014-01-26	Larry Meiners	3477026	107150	NULL	28871	E4980A	Agilent	001/710/710",
		"28870	2014-01-24	Dan Hosking	3477024	107137	NULL	28870	TDS744A	Tektronix	13/1F/1M/2F",
		"28860	2014-01-23	Christopher Reinhard	3477010	107125	NULL	28860	16555D	Agilent	W Cables/Terms",
		"28861	2014-01-23	Darious Clay	3477013	107127	NULL	28861	8596E	Agilent	004/041/105/151/160",
		"27957	2013-04-12	Christopher Reinhard	3475696	105627	NULL	27957	CMU300	Rohde & Schwarz	B12/B76/B78PCMCIA/K70/K71/K75/K76/K77/K78/K79/",
		"27958	2013-04-12	David Bither	3475697	105644	NULL	27958	CMU300	Rohde & Schwarz	B11/B21/B71/K31/K32/K33/K34/K39/K41",
		"27872	2013-03-28	Sandra Fletcher	3475588	105502	NULL	27872	CMU300	Rohde & Schwarz	B21/K41/PK30",
		"27850	2013-03-25	Jeron Powell	3475561	105472	NULL	27850	33120A	Agilent / HP	/001"
	]
	return header, data_lines


def _extract_from_selected_line(header: str, line: str):
	"""
	Extract equipment brand, model, and options from a tab-separated data line.
	
	This function parses a single equipment record and extracts the key information
	needed for analysis: brand name, model number, and available options.
	
	Args:
		header (str): Tab-separated column headers
		line (str): Tab-separated data line containing equipment information
		
	Returns:
		tuple: (brand, model, options)
			- brand (str): Equipment manufacturer name
			- model (str): Equipment model number
			- options (str): Available options (slash-separated)
	"""
	# Split header to create column name to index mapping
	head_cols = header.split("\t")
	col_to_idx = {name: i for i, name in enumerate(head_cols)}
	
	# Split the data line into individual fields
	parts = line.split("\t")
	
	# Safely get column indices for key fields
	idx_model = col_to_idx.get("eqModel")
	idx_brand = col_to_idx.get("eqBrand")
	idx_options = col_to_idx.get("options")
	
	# Extract values with bounds checking to prevent index errors
	brand = parts[idx_brand] if idx_brand is not None and idx_brand < len(parts) else ""
	model = parts[idx_model] if idx_model is not None and idx_model < len(parts) else ""
	options = parts[idx_options] if idx_options is not None and idx_options < len(parts) else ""
	
	return brand, model, options


def main():
	"""
	Main Streamlit application function.
	
	This function sets up the web interface, displays the equipment database,
	handles user interactions, and orchestrates the analysis workflow.
	"""
	# Display page title and description
	st.title(APP_TITLE)
	st.caption("Select equipment from the table below and click Analyze to see all the details")

	# Load the hardcoded equipment dataset
	header, all_data_lines = _get_hardcoded_data()

	# Create equipment selection interface
	if header and all_data_lines:
		st.markdown("---")
		st.subheader("📊 ATE Equipment Database")

		# Parse header for column names (not used in current implementation)
		header_cols = header.split("\t")

		# Create equipment selection interface
		st.markdown("**Select an equipment entry:**")

		# Create a list of display names for the radio buttons
		# Format: "📋 [Model] [Brand] - [Contact Name]"
		display_options = [f"📋 {line.split('\t')[7]} {line.split('\t')[8]} - {line.split('\t')[2]}" for line in all_data_lines]
		
		# Add a "Select equipment" placeholder at the beginning
		display_options.insert(0, "— Select equipment —")
		
		# Create radio button selection interface
		selected_display_option = st.radio(
			"Choose equipment:",
			options=display_options,
			index=0 # Default to the placeholder
		)
		
		# Market extraction is always enabled (previously had user toggle)
		do_market_extraction = True # Always perform market extraction now

		# Determine the selected equipment index based on the display option
		if selected_display_option == "— Select equipment —":
			selected_index = -1  # No equipment selected
		else:
			# Find the original index of the selected item
			# Subtract 1 because of the placeholder at index 0
			selected_index = display_options.index(selected_display_option) - 1
			
		# Process selected equipment if one is chosen
		if selected_index != -1:
			# Get the selected equipment data
			selected_line = all_data_lines[selected_index]
			parts = selected_line.split("\t")

			# Display selected equipment information
			st.markdown("---")
			st.subheader("🎯 Selected Equipment")

			# Show equipment details in two columns
			col1, col2 = st.columns(2)
			with col1:
				st.markdown(f"**Quote ID:** {parts[0]}")
				st.markdown(f"**Contact:** {parts[2]}")
				st.markdown(f"**Brand:** {parts[8]}")
				st.markdown(f"**Model:** {parts[7]}")
			with col2:
				st.markdown(f"**Created:** {parts[1]}")
				st.markdown(f"**Record ID:** {parts[4]}")
				st.markdown(f"**Options:** {parts[9]}")

			# Add analysis button
			st.markdown("---")
			check_clicked = st.button("🔍 Analyze", type="primary", use_container_width=True)

			# Check if we have cached analysis for this equipment to avoid re-processing
			brand_for_session = parts[8].strip()
			model_for_session = parts[7].strip()
			analysis_key_current = f"{brand_for_session}|{model_for_session}"
			cached_analysis = st.session_state.get("analysis_key") == analysis_key_current

			# Perform analysis if button clicked or if we have cached results
			if check_clicked or cached_analysis:
				# Show comprehensive loading state with non-technical explanations
				if check_clicked:
					st.markdown("---")
					st.subheader("🔍 Analyzing Your Equipment")
					
					# Display initial progress message
					st.info("🚀 I've started working. Please wait a bit for results...")

					# Add CSS for animated loading spinners
					st.markdown("""
					<style>
					@keyframes spin {
						0% { transform: rotate(0deg); }
						100% { transform: rotate(360deg); }
					}
					.spinning {
						animation: spin 1s linear infinite;
						display: inline-block;
					}
					</style>
					""", unsafe_allow_html=True)

					# Display first progress step: Parsing equipment data
					col1, col2 = st.columns([0.1, 0.9])
					with col1:
						# Show animated spinner
						st.markdown(
							"""
							<style>
							.spinner {
							  border: 4px solid #f3f3f3; /* Light gray */
							  border-top: 4px solid #3498db; /* Blue */
							  border-radius: 50%;
							  width: 22px;
							  height: 22px;
							  animation: spin 1s linear infinite;
							  margin: auto;
							}
							@keyframes spin {
							  0% { transform: rotate(0deg); }
							  100% { transform: rotate(360deg); }
							}
							</style>
							<div class="spinner"></div>
							""",
							unsafe_allow_html=True
						)
					with col2:
						st.write("**Parsing equipment data...**")

					# Extract brand/model/options from selected equipment line
					brand, model, options_str = _extract_from_selected_line(header, selected_line)
					brand_parsed = brand.strip()
					model_parsed = model.strip()

					# Parse and clean equipment options
					if options_str:
						# Split options by '/' and clean each option
						raw_options_list = [opt.strip() for opt in options_str.split('/') if opt.strip()]
						# Filter out any options that might be brand/model names
						filtered_options = []
						for opt in raw_options_list:
							# Skip if it looks like a brand or model name
							if opt.lower() not in [brand_parsed.lower(), model_parsed.lower()] and len(opt) > 0:
								filtered_options.append(opt)
						raw_options = '/'.join(filtered_options)
					else:
						raw_options = ""

					# AI-powered equipment analysis using OpenAI
					try:
						client = get_openai_client()
						# Create input string for AI processing
						llm_input = f"{brand_parsed} {model_parsed} {raw_options}" if raw_options else f"{brand_parsed} {model_parsed}"
						
						if client is not None:
							# Use AI to normalize and parse equipment options
							payload = normalize_options_via_llm(
								client,
								llm_input,
								MODEL_NAME,
								float(TEMPERATURE),
							)
						else:
							# Fallback to deterministic parsing if no AI client
							payload = {
								"normalized": {
									"brand": brand_parsed,
									"model": model_parsed,
									"options": split_options_deterministic(raw_options)
								},
								"results": []
							}
						# Ensure brand and model are set correctly
						payload["normalized"]["brand"] = brand_parsed
						payload["normalized"]["model"] = model_parsed
					except Exception as e:
						# Handle AI processing errors gracefully
						payload = {
							"normalized": {
								"brand": brand_parsed,
								"model": model_parsed,
								"options": []
							},
							"results": []
						}

					# Step 2: Generate AI explanations for each equipment option
					col1, col2 = st.columns([0.1, 0.9])
					with col1:
						# Show animated spinner for options explanation
						st.markdown(
							"""
							<style>
							.spinner {
							  border: 4px solid #f3f3f3; /* Light gray */
							  border-top: 4px solid #3498db; /* Blue */
							  border-radius: 50%;
							  width: 22px;
							  height: 22px;
							  animation: spin 1s linear infinite;
							  margin: auto;
							}
							@keyframes spin {
							  0% { transform: rotate(0deg); }
							  100% { transform: rotate(360deg); }
							}
							</style>
							<div class="spinner"></div>
							""",
							unsafe_allow_html=True
						)
					with col2:
						st.write("**Explaining options...**")

					# Generate detailed explanations for each equipment option using AI
					options_list = payload.get("normalized", {}).get("options", []) or []
					option_explanations = {}
					client_for_opts = get_openai_client() # Reuse OpenAI client for option explanations
					
					if options_list:
						brand_for_opts = payload.get("normalized", {}).get("brand", "")
						model_for_opts = payload.get("normalized", {}).get("model", "")
						
						# Generate explanation for each option
						for opt in options_list:
							try:
								if client_for_opts is not None:
									# Create detailed prompt for option explanation
									opt_prompt = (
										f"Explain briefly what option '{opt}' means for {brand_for_opts} {model_for_opts}. "
										"Include what it adds or changes, typical functionality, and any compatibility considerations. "
										"Answer in 3-5 concise sentences in simple terms."
									)
									# Call OpenAI API for option explanation
									opt_completion = client_for_opts.chat.completions.create(
										model=MODEL_NAME,
										temperature=float(TEMPERATURE),
										messages=[
											{"role": "system", "content": "You are a helpful expert explaining test equipment options in simple terms."},
											{"role": "user", "content": opt_prompt},
										],
									)
									option_explanations[opt] = opt_completion.choices[0].message.content or "No explanation available."
								else:
									# Fallback explanation if no AI client available
									option_explanations[opt] = f"Option '{opt}' adds specific functionality to the {brand_for_opts} {model_for_opts}."
							except Exception as e:
								# Handle errors in option explanation generation
								option_explanations[opt] = f"Could not get details for option '{opt}': {e}"

					# Step 3: Searching market data
					# col1, col2 = st.columns([0.05, 0.95])
					# with col1:
					# 	st.markdown(
					# 		"""
					# 		<style>
					# 		.spinner {
					# 		  border: 4px solid #f3f3f3; /* Light gray */
					# 		  border-top: 4px solid #3498db; /* Blue */
					# 		  border-radius: 50%;
					# 		  width: 22px;
					# 		  height: 22px;
					# 		  animation: spin 1s linear infinite;
					# 		  margin: auto;
					# 		}
					# 		@keyframes spin {
					# 		  0% { transform: rotate(0deg); }
					# 		  100% { transform: rotate(360deg); }
					# 		}
					# 		</style>
					# 		<div class="spinner"></div>
					# 		""",
					# 		unsafe_allow_html=True
					# )
					# with col2:
					# 	st.write("**Searching market data...**")

					# Web scraping
					scraping_results = None
					if do_market_extraction:
						try:
							# Use the effective scraper to find equipment listings and prices
							scraping_results = scrape_effective_sites(
								brand_parsed,
								model_parsed,
								payload["normalized"]["options"]
							)
						except Exception as e:
							# Handle scraping errors gracefully
							scraping_results = None
					else:
						st.info("Market data extraction skipped.")

					# Define analysis steps for progress display
					steps = [
						"Parsing equipment data",
						"Explaining options",
						# "Searching market data"  # Commented out in UI but functionality exists
					]

					# Display completion status for each analysis step
					for step in steps:
						col1, col2 = st.columns([0.05, 0.95])  # smaller gap
						with col1:
							# if step == "Searching market data" and not do_market_extraction:
							# 	st.markdown("➖") # Use a different icon for skipped step
							# else:
							st.markdown("✅")
						with col2:
							st.markdown(
								f"<span style='font-size:16px; font-weight:600;'>{step}</span>",
								unsafe_allow_html=True
							)

					# Store analysis results in session state for caching and display
					st.session_state["analysis_key"] = f"{brand_parsed}|{model_parsed}"
					st.session_state["analysis_payload"] = payload
					# Only store scraping results if market extraction was performed
					st.session_state["analysis_scraping"] = scraping_results if do_market_extraction else None
					st.session_state["option_explanations"] = option_explanations

				# Display complete analysis results (only after everything is ready)
				if st.session_state.get("analysis_key") == analysis_key_current:
					# Retrieve cached analysis results from session state
					payload = st.session_state.get("analysis_payload")
					scraping_results = st.session_state.get("analysis_scraping")
					option_explanations = st.session_state.get("option_explanations", {})

					# Display results section
					st.markdown("---")
					st.subheader("📋 Complete Analysis Results")

					# Show raw parsing results in JSON format
					st.markdown("**✅ Equipment Analysis:**")
					st.code(json.dumps(payload, indent=2), language="json")

					# Options explorer with tabular display
					options_list = payload.get("normalized", {}).get("options", []) or []
					st.markdown("**🔧 Options Explorer:**")
					
					if not options_list:
						st.info("No options found for this equipment model.")
					else:
						# Create table data with AI-determined categories for each option
						table_data = []
						for i, opt in enumerate(options_list):
							explanation = option_explanations.get(opt, "No description available.")
							
							# Use AI to categorize each option for better organization
							category = "General"  # Default category
							try:
								if client_for_opts is not None:
									# Create prompt for option categorization
									category_prompt = (
										f"Based on this option description: '{explanation}' for option '{opt}', "
										f"categorize it into one of these categories: Connectivity, Software, Calibration, Power, Display, Storage, Communication, or General. "
										f"Respond with only the category name, nothing else."
									)
									# Call AI for categorization
									category_completion = client_for_opts.chat.completions.create(
										model=MODEL_NAME,
										temperature=0.1,  # Lower temperature for more consistent categorization
										messages=[
											{"role": "system", "content": "You are a helpful expert that categorizes test equipment options. Respond with only the category name."},
											{"role": "user", "content": category_prompt},
										],
									)
									api_category = category_completion.choices[0].message.content.strip()
									# Validate the category is one of our predefined ones
									valid_categories = ["Connectivity", "Software", "Calibration", "Power", "Display", "Storage", "Communication", "General"]
									if api_category in valid_categories:
										category = api_category
							except Exception as e:
								category = "General"  # Fallback to default category
							
							# Add option data to table
							table_data.append({
								"Row": i + 1,
								"Option Code": opt,
								"Category": category,
								"Description": explanation
							})

						# Generate Markdown table for options display
						markdown_table = "**All available options for this equipment:**\n\n"
						markdown_table += "| Row | Option Code | Category | Description |\n"
						markdown_table += "|-----|-------------|----------|-------------|\n"
						
						# Add each option row to the table
						for row_data in table_data:
							# Escape pipe characters in description to prevent breaking table format
							description = str(row_data['Description']).replace("|", "\\|")
							markdown_table += f"| {row_data['Row']} | {row_data['Option Code']} | {row_data['Category']} | {description} |\n"
						
						# Display the formatted table
						st.markdown(markdown_table)

					# Display market data results (if available)
					if do_market_extraction:
						# Note: Market data display is currently commented out in the UI
						# but the data is still collected and could be displayed
						scraping_json = {"web_scraping_results": []}
						if scraping_results and "search_results" in scraping_results and scraping_results["search_results"]:
							# Process and format market data results
							for result in scraping_results["search_results"]:
								scraping_json["web_scraping_results"].append({
									"brand": result.get('brand', 'N/A'),
									"model": result.get('model', 'N/A'),
									"price": result.get('price', 'Price not available'),
									"vendor": result.get('vendor', 'Vendor not available'),
									"web_url": result.get('web_url', 'URL not available'),
									"qty_available": result.get('qty_available', 'Quantity not available'),
									"source": result.get('source', 'Source not available')
							})
						# Note: Market data JSON display is commented out
						# st.code(json.dumps(scraping_json, indent=2), language="json")
			else:
				# Show message when no equipment is selected
				st.info("👆 Please select an equipment entry from the dropdown above.")
	else:
		# Show error if no dataset is available
		st.error("No dataset available.")


if __name__ == "__main__":

	main()
