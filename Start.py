import inquirer

print('')
print('Welcome to Binance Trading Bot')
print('')
print('By CryptoCaru 2019')
print('')

questions = [
  inquirer.List('App',
                message="What do you want to do?",
                choices=['Live', 'Backtest', 'Trading History'],
            ),
]
answers = inquirer.prompt(questions)
answers = answers['App'] 
print(answers)
print('')

if answers == 'Backtest':
	import Backtest
elif answers == 'Live':
	import Live
elif answers == 'Trading History':
	import TradeHistory
	
