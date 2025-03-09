import argparse
import json
from flask_cors import CORS  # Add this import
from flask import Flask, request, jsonify
from core_functions import (
    main as cli_main,
    client_creation,
    build_messages,
    execute_chat_completion,
    process_api_response_and_validate,
    handle_api_errors,
    retrieve_api_keys_based_on_api_selection
)

# Mode switching implementation
def setup_api_server():
    """Configure and return the Flask application for API mode"""
    app = Flask(__name__)
    CORS(app)
    @app.route('/process', methods=['POST'])
    def api_handler():
        """Endpoint for automated card data processing"""
        # Validate input
        if not request.is_json:
            return jsonify({"error": "Request must be JSON"}), 400
            
        data = request.get_json()
        print(data)
        
        # Validate required parameters
        required_fields = ['card_choice', 'selected_api', 'selected_model']
        if missing := [field for field in required_fields if field not in data]:
            return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400
        
        try:
            # Extract parameters
            card_choice = data['card_choice']
            selected_api = data['selected_api']
            selected_model = data['selected_model']

            OPENAI_KEY, PERPLEXITY_KEY = retrieve_api_keys_based_on_api_selection(selected_api)
            
            #Client creation
            client = client_creation(selected_api, OPENAI_KEY, PERPLEXITY_KEY)
            
            # Build messages structure
            messages = build_messages(selected_api, card_choice)
            
            # Execute API call
            completion, api_success = execute_chat_completion(
                client, selected_api, selected_model, messages
            )
            if not api_success:
                return jsonify({"error": "API communication failed"}), 502
                
            # Process response
            response_text = completion.choices[0].message.content
            # In the api_handler function:
            success = process_api_response_and_validate(completion,selected_api, response_text)

            if success:
                # Directly use the validated JSON from response_text
                return jsonify(json.loads(response_text)), 200
            else:
                return jsonify({"error": "Data validation failed"}), 422
                
        except Exception as e:
            handle_api_errors(e, selected_api)
            return jsonify({"error": str(e)}), 500
    
    return app

def parse_arguments():
    """Handle command-line arguments for mode selection"""
    parser = argparse.ArgumentParser(
        description="Credit Card Data Processor",
        epilog="Modes: manual (CLI) | auto (API server)"
    )
    parser.add_argument('--mode', 
        choices=['manual', 'auto'], 
        default='manual',
        help="Operation mode (default: manual)"
    )
    parser.add_argument('--host', 
        default='0.0.0.0',
        help="API server host (default: 0.0.0.0)"
    )
    parser.add_argument('--port', 
        type=int,
        default=5000,
        help="API server port (default: 5000)"
    )
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_arguments()
    
    if args.mode == 'manual':
        # Run CLI version
        cli_main()
    else:
        # Start API server
        app = setup_api_server()
        app.run(
            host=args.host,
            port=args.port,
            debug=False
        )
        print(f"API server running on {args.host}:{args.port}")
