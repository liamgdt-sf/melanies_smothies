# Import python packages
import streamlit as st
import pandas as pd

import requests

from urllib.parse import quote

# from snowflake.snowpark.context import get_active_session
from snowflake.snowpark.functions import col 


# Write directly to the app
st.title(f":cup_with_straw: Customize Your Smoothie!:cup_with_straw:")
st.write(
  """Choose the fruits you want in your custom Smoothie!.
  """
)


cnx = st.connection('snowflake')
session = cnx.session()    # get_active_session()



name_on_order = st.text_input('Name on Smoothie:')
# Currently no apostrophes tolerated in name

st.write('The name on your Smoothie will be :' , name_on_order)


my_dataframe = session.table('smoothies.public.fruit_options'
                            ).select(col('FRUIT_NAME') , col('search_on'))

# st.dataframe(data=my_dataframe , use_container_width=True)
# st.stop()

pd_df = my_dataframe.to_pandas()
st.dataframe(pd_df)


# st.stop()

ingredient_list = st.multiselect('Chose up to 5 ingredients' ,
                                my_dataframe ,
                                max_selections=5)

if ingredient_list:
    ingredient_string = ''

    for fruit_chosen in ingredient_list:
        ingredient_string += fruit_chosen + ' '
        search_on=pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        st.write(f'The search value for "{fruit_chosen}" is "{search_on}".')

        search_on = quote(search_on)
        st.subheader(fruit_chosen + ' Nutritional Information:')
        st.write(f"https://my.smoothiefroot.com/api/fruit/{search_on}")
        smoothiefroot_response = requests.get(f"https://my.smoothiefroot.com/api/fruit/{search_on}")
        
        st.write(smoothiefroot_response.json())

        a = pd.DataFrame.from_dict([smoothiefroot_response.json()])
        st.dataframe(a , hide_index=True)
        a.index.rename('nutrients' , inplace= True)
        a.reset_index(inplace=True)
        a['nutrients'] = a['nutrients'].str.title()
        a.drop(columns = ['family' , 'genus' , 'id' , 'name' , 'order'], inplace = True)
        st.dataframe(a , hide_index=True)
        

        # sf_df = st.dataframe(smoothiefroot_response.json() , use_container_width=True)

    # st.write(ingredient_string)

    my_insert_stmt = """INSERT INTO smoothies.public.orders(ingredients , name_on_order) 
                        VALUES ('""" + ingredient_string + """','""" + name_on_order + """ ')"""

    # st.write(my_insert_stmt)
    # st.stop()       # GOOD FOR HALTING EXECUTION , DEBUGGING
    

    time_to_insert = st.button('Submit Order')

    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success(f'Your Smoothie is ordered, {name_on_order}!' , icon = '✅')


