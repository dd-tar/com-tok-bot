welcome_text = f"I am a bot that will help create and manage your tokenized community or DAO.\n\n" + \
               "That\'s what I can do:\n\n" + \
               "/create\_token - creating a community token with the name, symbol, and price you specified in arguments." \
               " You will be able to exchange your token to a native network token, " \
               "change the price at which the exchange takes place, and much more. " \
               "The token contract also inherits the ERC20Votes standard, " \
               "so you can use the token for community votes in [Snapshot](https://snapshot.org/#/).\n" \
               "\n_Arguments_: Name Symbol Price\n" + \
               "_Example_: `/create_token MyTokenName MTN 0.05`\n\n" + \
               "/mint\_tokens - mint your community token in exchange for a native network token (ETH). " \
               "All ETH received from the token exchange will be sent to the address " \
               "of the owner (creator) of the token.\n" + \
               "\n_Arguments_: token\_address amount\n" + \
               "_Example_: `/mint_tokens 0x0000000000000000000000000000000000000000 0.5`\n\n" + \
               "/change\_token\_price - changing the exchange rate of your token." \
               " This method is only available to the token owner.\n" + \
               "\n_Arguments_: token\_address new\_price\n" + \
               "_Example_: `/change_token_price 0x0000000000000000000000000000000000000000 0.07`\n\n" + \
               "/join\_group - getting a personal link to join a community chat after checking for the presence " \
               "of a community token from the user address.  " \
               "If you don\'t have a community chat\_id, you need a link created via " \
               "/get\_join\_deeplink by community members.\n" + \
               "\n_Arguments_: chat\_id user\_address\n" + \
               "_Example_: `/join_group -3141592 0x0000000000000000000000000000000000000000`\n\n" + \
               "/add\_community\_token - setting a community token for a chat, the presence of which will be checked " \
               "when joining the chat via the link.\n" \
               "_Note: These can be any tokens that have a standard balanceOf() method, including ERC721, " \
               "not only created through this bot._\n\[group chat only]\n" + \
               "\n_Arguments_: token\_address \n" + \
               "_Example_: `/add_community_token 0x0000000000000000000000000000000000000000`\n\n" + \
               "/get\_community\_token\_address - it will remind you of the community token address set in this chat." \
               "\n\[group chat only]\n" + \
               "\n_No arguments_\n" + \
               "_Example_: `/get_community_token_address`\n\n" + \
               "/delete\_community\_token - remove the community token for this chat.\n\[group chat only]\n" + \
               "\n_No arguments_\n" + \
               "_Example_: `/delete_community_token`\n\n" + \
               "/get\_mint\_deeplink - create an invite link to mint the community token.\n" \
               "When clicking on the link, the user will be redirected to a dialog with the bot, " \
               "which will send him a link to mint of the specified number of community tokens after" \
               " clicking the start button. \n\[group chat only]\n" + \
               "\n_Arguments_: amount\n" + \
               "_Example_: `/get_mint_deeplink 9.5`\n\n" + \
               "/get\_join\_deeplink - create an invite link to join the community chat.\nBefore sending the link, " \
               "the bot will ask the user to confirm that the specified address belongs to him and will check that " \
               "this address owns at least 1 community token. \n\[group chat only]\n" + \
               "\n_No arguments_\n" + \
               "_Example_: `/get_join_deeplink`\n\n" + \
               "/help or /start - send this message\n\n" \
               "_Note: All functions that require signing a transaction or message will redirect you to the site," \
               " where the MetaMask wallet window will automatically open._"
