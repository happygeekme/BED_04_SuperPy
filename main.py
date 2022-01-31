# Imports
import argparse
import csv
from datetime import date, datetime, timedelta
from rich import print as rprint
from rich.console import Console
from rich.table import Table 

# Do not change these lines.
__winc_id__ = "a2bc36ea784242e4989deb157d527ba0"
__human_name__ = "superpy"


# Your code below this line.
def main():
    console = Console()
    today = str(date.today())
    delta1 = timedelta(days=1)
    fieldnames = ['id', 'product', 'buy_price', 'buy_date', 'expiration_date', 'sold', 'sell_price']

    # check if format date is correct
    def validate_date(date_text:str):
        try:
            datetime.strptime(date_text, '%Y-%m-%d')
        except ValueError:
            raise ValueError('Incorrect date format, date should be given as yyyy-mm-dd')

    def yes_or_no(answer):
        try: 
            if answer not in 'yn':
                raise ValueError('Please enter "y" for yes and "n" for no')
        except:
            raise ValueError('Please enter "y" for yes and "n" for no')

    
# CSV READER AND WRITING

    # create id
    def get_id(file):
        with open(file, 'r') as csv_file:
            reader = csv.reader(csv_file)
            reader_list = list(reader)
            id = len(reader_list)
            return id

    # append line to existing csv file
    def append_to_csv(csv_file: str, new_item: dict):
        with open(csv_file, 'a', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writerow(new_item)

    # read bought, include sell information and save to temp
    def add_sale_temp(sold_product):
        with open('bought.csv', 'r') as csvfile:
            reader = csv.DictReader(csvfile)

            with open('temp.csv', 'w', newline='') as temp:
                # fieldnames = list(sold_product.keys())
                writer = csv.DictWriter(temp, fieldnames=fieldnames)
                writer.writeheader()

                for row in reader:
                    if row['id'] == sold_product['id']:
                        row['sold'] = today
                        row['sell_price'] = args.sell_price[0]
                    writer.writerow(row)

    # copy temp file to bought file
    def copy_temp_to_bought():
        with open('temp.csv', 'r', newline='') as temp:
            reader = csv.DictReader(temp)

            with open('bought.csv', 'w', newline='') as bought:
                writer = csv.DictWriter(bought, fieldnames=fieldnames)
                writer.writeheader()

                for row in reader:
                    writer.writerow(row)

    # create line (dict) to add to bought.csv
    def bought(args):
        print('bought action')
        validate_date(args.expiration_date)
        new_item = {}
        new_item['id'] = get_id('bought.csv')
        new_item['product'] = args.product[0].lower()
        new_item['buy_price'] = args.buy_price[0]
        new_item['buy_date'] = today
        new_item['expiration_date'] = args.expiration_date
        new_item['sold'] = 'not'
        new_item['sell_price'] = '0'
        append_to_csv('bought.csv', new_item)

    # create line (dict) to add to sold.csv, add to temp, then copy temp to bought
    def sell(args):
        print('sell action')
        with open('bought.csv', 'r', newline='') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            items_to_be_sold = []
            # find item to be sold
            for line in csv_reader:
                if (line['product'] == args.product) and (line['sold'] == 'not') and (line['expiration_date'] >= today):
                    items_to_be_sold.append(line)
            # if not available print 'sold out'
            if len(items_to_be_sold) < 1:
                print('This item is sold out')
            # if available select most perisable item & create item for sold list
            else:                
                expiration_sorted = sorted(
                    items_to_be_sold, key=lambda k: k['expiration_date'])
                # append item to sold list    
                sold_product = expiration_sorted[0]
                # adjust sold information in bought list
                add_sale_temp(sold_product)
                copy_temp_to_bought()

    # search expired products on date specified by user
    def expired(args):
        print('expired action')
        if args.now == True:
            d = today
        if args.yesterday == True:
            d = str(date.today() - delta1)
        if args.advance_time != None:
            delta = timedelta(days=args.advance_time[0])
            d = str(date.today() + delta)
        if args.date != None:
            validate_date(args.date)
            d = args.date
           
        with open('bought.csv', 'r', newline='') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            expired = []
            total_cost = 0.00

            for line in csv_reader:
                if (line['sold'] == 'not') and (line['expiration_date'] == d):
                    expired.append(line)

            if len(expired) < 1:
                rprint(f'Nothing expired {d}')
            else:
                rprint(f'The following items will expire {d}')                
                table = Table(show_header=True, header_style="bold medium_turquoise", border_style="medium_turquoise" )
                table.add_column("id", style="dim")
                table.add_column("Product", style="aquamarine3", width=12)
                table.add_column('Bought', style="aquamarine3", width=12)
                table.add_column('Cost', width=12, justify="right", style="indian_red1")
                for item in expired:
                    total_cost += float(item['buy_price'])
                    table.add_row(
                        item['id'],
                        item['product'],
                        item['buy_date'],
                        item['buy_price']
                        )
                table.add_row('', '[indian_red1]Total costs[/indian_red1]', f'[indian_red1]{d}[/indian_red1]', "{:.2f}".format(total_cost))
                console.print(table)
                
                question = input ('Do you want to save this to a file? y / n : ')
                answer = question.lower()
                yes_or_no(answer)
                if answer == 'y':
                    filename = 'expired_'+d+'.csv'
                    for line in expired:                    
                        append_to_csv(filename, line)

    # check inventory on date specified by user
    def inventory(args):
        print('inventory action')
        if args.now == True:
            d = today
        if args.yesterday == True:
            d = str(date.today() - delta1)
        if args.date != None:
            validate_date(args.date)
            d = args.date
        
        with open('bought.csv', 'r', newline='') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            inventory = []

            for line in csv_reader:
                if (line['buy_date'] <= d) and (line['sold'] == 'not') and (line['expiration_date'] > d):
                    inventory.append(line)
            if len(inventory) < 1:
                 rprint(f'No inventory information for {d}')
            else:   
                rprint(f'inventory {d}')
                table = Table(show_header=True, header_style="bold medium_turquoise", border_style="medium_turquoise" )
                table.add_column("id", style="dim")
                table.add_column("Product", style="aquamarine3", width=12)
                table.add_column('Buy Date', style="aquamarine3", justify="center", width=14)
                table.add_column('Buy Price', width=12, justify="center", style="indian_red1")
                table.add_column('Expiration Date', style="aquamarine3", justify="center", width=16)
                for item in inventory:
                    table.add_row(
                        item['id'],
                        item['product'],
                        item['buy_date'],
                        "{:.2f}".format(float(item['buy_price'])),
                        item['expiration_date']
                        )
                console.print(table)
                
                question = input ('Do you want to save this to a file? y / n : ')
                answer = question.lower()
                yes_or_no(answer)
                filename = 'inventory_'+d+'.csv'
                for line in inventory:                    
                    append_to_csv(filename, line)

            
    def revenue(args):
        print('revenue action')
        if args.now == True:
            d = today
        if args.yesterday == True:
            d = str(date.today() - delta1)
        if args.date != None:
            validate_date(args.date)
            d = args.date
        
        with open('bought.csv', 'r', newline='') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            sold_today = []

            for line in csv_reader:
                if line['sold'] == d:
                    sold_today.append(line)

            if len(sold_today) < 1:
                rprint(f'No revenue {d}')
            else:
                revenue = 0.00
                for item in sold_today:
                    revenue +=  float(item['sell_price'])
                rprint(f'revenue for {d}: {revenue}')
                table = Table(show_header=True, header_style="bold medium_turquoise", border_style="medium_turquoise" )
                table.add_column("id", style="dim")
                table.add_column("Product", style="aquamarine3", width=12)
                table.add_column('Buy Date', style="aquamarine3", justify="center", width=14)
                table.add_column('Buy Price', width=12, justify="center", style="indian_red1")
                table.add_column('Sell Price', style="sea_green2", justify="center", width=16)
                for item in sold_today:
                    table.add_row(
                        item['id'],
                        item['product'],
                        item['buy_date'],
                        "{:.2f}".format(float(item['buy_price'])),
                         "{:.2f}".format(float(item['sell_price']))
                        )
                table.add_row('', '[sea_green2]Total sold[/sea_green2]', '', '', "{:.2f}".format(revenue))
                console.print(table)
                question = input ('Do you want to save this to a file? y / n : ')
                answer = question.lower()
                yes_or_no(answer)
                if answer == 'y':
                    filename = 'revenue_'+d+'.csv'
                    for line in revenue:                    
                        append_to_csv(filename, line)


    def profit(args):
        print('profit action')
        if args.now == True:
            d = today
        if args.yesterday == True:
            d = str(date.today() - delta1)
        if args.date != None:
            validate_date(args.date)
            d = args.date
        
        with open('bought.csv', 'r', newline='') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            sold_today = []
            expired_today = []

            for line in csv_reader:
                if line['sold'] == d:
                    sold_today.append(line)
                elif line['expiration_date'] == d and line['sold'] == 'not':
                    expired_today.append(line)
            
            revenue = 0.00
            costs = 0.00
            expired = 0.00
            
            for item in expired_today:
                expired += float(item['buy_price'])
            
            if len(sold_today) >= 1:                          
                for item in sold_today:
                    revenue +=  float(item['sell_price'])
                    costs += float(item['buy_price'])
                profit = revenue - costs - expired
              
                table = Table(show_header=True, header_style='bold medium_turquoise', border_style='medium_turquoise' )
                table.add_column(d)
                table.add_column('eur')
                table.add_row('Revenue', "{:.2f}".format(revenue))
                table.add_row('Buy Costs sales', "{:.2f}".format(costs))
                table.add_row('Costs due expired products', "{:.2f}".format(expired))
                if profit > 0:
                    table.add_row(f'[sea_green2]Total profit {d}[/sea_green2]', "[sea_green2]{:.2f}[/sea_green2]".format(profit))
                else:
                    table.add_row(f'[indian_red1]No profit {d}[/indian_red1]', "[indian_red1]{:.2f}[/indian_red1]".format(profit))    
                console.print(table)

                question = input ('Do you want to save this to a file? y / n : ')
                answer = question.lower()
                yes_or_no(answer)
                if answer == 'y':
                    filename = 'profit_'+d+'.csv'
                    for line in sold_today:                    
                        append_to_csv(filename, line)

            else:
                rprint(f'No sales {d}')
                if len(expired_today) >= 1:
                    rprint(f'Cost due expired products {d}: {expired}')
           

    # --------------------------------------------------------------------------------------------
    # ARGUMENT PARSER
    parser = argparse.ArgumentParser(prog='SuperPy', description='Supermarket Inventory Tool')

    # inventory parsers
    subparsers = parser.add_subparsers(help='Choose one of the positional arguments. Add items to your inventory see "buy -h", sell items from your inventory see "sel -h", check inventory see "inventory -h", check expired products see "expird -h", check revenue see "revenue -h", and check profit see "profit -h"')

    # add a product to inventory
    buy_parser = subparsers.add_parser('buy')
    buy_parser.add_argument('buy', help='add product to inventory: buy [productname] [buy pice] [expiration date]', action='store_true')
    buy_parser.add_argument('product', help='product name', nargs=1)
    buy_parser.add_argument('buy_price', help='price the product is bought for', nargs=1, type=float)
    buy_parser.add_argument('expiration_date', help='expiration date as yyyy-mm-dd')
    buy_parser.set_defaults(func=bought)

    # sell a product from inventory
    sell_parser = subparsers.add_parser('sell')
    sell_parser.add_argument('sell', help='sell product from inventory: sell [product name] [sell price]', action='store_true')
    sell_parser.add_argument('product', help='product name')
    sell_parser.add_argument('sell_price', help='price the product is sold for', nargs=1, type=float)
    sell_parser.set_defaults(func=sell)

    # parent parser for dates
    date_parent_parser = subparsers.add_parser('date', add_help=False)
    date_parent_parser.add_argument('-now', help='at this moment', action='store_true')
    date_parent_parser.add_argument('-yesterday', help='set date to yesterday', action='store_true')
    date_parent_parser.add_argument('-date',metavar='', help='specify date as yyyy-mm-dd')


    # check expired products by date
    expired_parser = subparsers.add_parser('expired', parents=[date_parent_parser])
    expired_parser.add_argument('expired', help='check expired products: expired [your date choice], date choices -> today, yesterday, date specified or number of days after today. See optional arguments below.', action='store_true')
    expired_parser.add_argument('-advance_time', metavar='', help='expired -advance_time [number of days]. Check which products will expire a specified number of days in the future.', nargs=1, type=int)
    expired_parser.set_defaults(func=expired)

    # report inventory
    inventory_parser = subparsers.add_parser('inventory', parents=[date_parent_parser])
    inventory_parser.add_argument('inventory', help='check inventory: inventory [your date choice], date choices -> now, yesterday or on the date specified, see optional arguments below.', action='store_true')
    inventory_parser.set_defaults(func=inventory)


    # report revenue
    revenue_parser = subparsers.add_parser('revenue', parents=[date_parent_parser])
    revenue_parser.add_argument('revenue', help='check revenue: revenue [your date choice], date choices -> today, yesterday or date specified, see optional arguments below.', action='store_true')
    revenue_parser.set_defaults(func=revenue)

    # report profit
    profit_parser = subparsers.add_parser('profit', parents=[date_parent_parser])
    profit_parser.add_argument('profit', help='check profit: profit [your date choice], date choices -> now, yesterday or on the date specified, see optional arguments below.', action='store_true')
    profit_parser.set_defaults(func=profit)

    args = parser.parse_args()


    if args.func:
        args.func(args)


if __name__ == "__main__":
    main()
