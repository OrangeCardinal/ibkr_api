from enum import Enum
class Messages(object):

        field_types = Enum( INTEGER=1,
                            STRING = 2,
                            FLOAT = 3)
        inbound = {
            'tick_price':1,'tick_size':2,'order_status':3,'err_msg':4,'open_order':5,
            'acct_value':6,'portfolio_value':7,'acct_update_time':8,'next_valid_id':9,
            'contract_data':10,'execution_data':11,'market_depth':12,'market_depth_l2':13,
            'neWs_bulletins':14,'managed_accts':15,'receive_fa':16,'historical_data':17,
            'bond_contract_data':18,'scanner_parameters':19,'scanner_data':20,'tick_option_computation':21,
            'tick_generic':45,'tick_string':46,'tick_efp':47,'current_time':49,
            'real_time_bars':50,'fundamental_data':51,'contract_data_end':52,'open_order_end':53,
            'acct_doWnload_end':54,'execution_data_end':55,'delta_neutral_validation':56,'tick_snapshot_end':57,
            'market_data_type':58,'commission_report':59,'position_data':61,'position_end':62,
            'account_summary':63,'account_summary_end':64,'verify_message_api':65,'verify_completed':66,
            'display_group_list':67,'display_group_updated':68,'verify_and_auth_message_api':69,'verify_and_auth_completed':70,
            'position_multi':71,'position_multi_end':72,'account_update_multi':73,'account_update_multi_end':74,
            'security_definition_option_parameter':75,'security_definition_option_parameter_end':76,'soft_dollar_tiers':77,
            'family_codes':78,'symbol_samples':79,'mkt_depth_exchanges':80,'tick_req_params':81,'smart_components':82,
            'neWs_article':83,'tick_neWs':84,'neWs_providers':85,'historical_neWs':86,
            'historical_neWs_end':87,'head_timestamp':88,'histogram_data':89,'historical_data_update':90,
            'reroute_mkt_data_req':91,'reroute_mkt_depth_req':92,'market_rule':93,'pnl':94,
            'pnl_single':95,'historical_ticks':96,'historical_ticks_bid_ask':97,'historical_ticks_last':98,
            'tick_by_tick':99,'order_bound':100}

        outbound = {
            'req_mkt_data':1,'cancel_mkt_data':2,'place_order':3,'cancel_order':4,'req_open_orders':5,'req_acct_data':6,
            'req_executions':7,'req_ids':8,'req_contract_data':9,'req_mkt_depth':10,'cancel_mkt_depth':11,'req_neWs_bulletins':12,
            'cancel_neWs_bulletins':13,'set_server_loglevel':14,'req_auto_open_orders':15,'req_all_open_orders':16,
            'req_managed_accts':17,'req_fa':18,'replace_fa':19,'req_historical_data':20,'exercise_options':21,'req_scanner_subscription':22,
            'cancel_scanner_subscription':23,'req_scanner_parameters':24,'cancel_historical_data':25,'req_current_time':49,
            'req_real_time_bars':50,'cancel_real_time_bars':51,'req_fundamental_data':52,'cancel_fundamental_data':53,
            'req_calc_implied_volat':54,'req_calc_option_price':55,'cancel_calc_implied_volat':56,'cancel_calc_option_price':57,
            'req_global_cancel':58,'req_market_data_type':59,'req_positions':61,'req_account_summary':62,'cancel_account_summary':63,
            'cancel_positions':64,'verify_request':65,'verify_message':66,'query_display_groups':67,'subscribe_to_group_events':68,
            'update_display_group':69,'unsubscribe_from_group_events':70,'start_api':71,'verify_and_auth_request':72,
            'verify_and_auth_message':73,'req_positions_multi':74,'cancel_positions_multi':75,'req_account_updates_multi':76,
            'cancel_account_updates_multi':77,'req_sec_def_opt_params':78,'req_soft_dollar_tiers':79,'req_family_codes':80,
            'req_matching_symbols':81,'req_mkt_depth_exchanges':82,'req_smart_components':83,'req_neWs_article':84,
            'req_neWs_providers':85,'req_historical_neWs':86,'req_head_timestamp':87,'req_histogram_data':88,'cancel_histogram_data':89,
            'cancel_head_timestamp':90,'req_market_rule':91,'req_pnl':92,'cancel_pnl':93,'req_pnl_single':94,'cancel_pnl_single':95,
            'req_historical_ticks':96,'req_tick_by_tick_data':97,'cancel_tick_by_tick_data':98}