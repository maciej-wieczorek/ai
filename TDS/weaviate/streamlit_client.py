#todo: doinstaluj streamlit i pandas jeÅ›li jeszcze nie masz ich zainstalowanych
import pandas as pd
import streamlit as st
import warnings
warnings.filterwarnings("ignore")

import weaviate
client = weaviate.Client("http://localhost:8080")

#todo: 2.a przygotuj zapytanie ktÃ³re zwrÃ³ci 22 frazy ktÃ³re sÄ… jednoczeÅ›nie:
# podobne do sÅ‚Ã³w "vocation", "values"
# niepodobne do sÅ‚Ã³w "vices", "rot", "debauchery"
# krÃ³tsze niÅ¼ 3 sÅ‚owa
# majÄ… minimalnÄ… pewnoÅ›Ä‡ 0.22

where_filter = {
}

near_text_filter = {
}

query_result = client.query\
    .get("Synonym", ["text"])\
    #twoje zaptyanie powinno byÄ‡ kontynuowane tutaj


#todo: 2.b wyÅ›wietl wyniki zapytania razem z ich pewnoÅ›ciÄ… ('certainity') w formie DataFrame


#todo: 2.c przygotuj zapytanie ktÃ³re zwrÃ³ci 33 frazy ktÃ³re sÄ… jednoczeÅ›nie:
# NIEpodobne do sÅ‚Ã³w "values", "joy"
# podobne do sÅ‚Ã³w "vices", "debauchery"
# sÄ… krÃ³tsze niÅ¼ 2 sÅ‚owa
# majÄ… minimalnÄ… pewnoÅ›Ä‡ 0.33


#todo: 2.d wyÅ›wietl (przy uÅ¼yciu streamlit) wyniki zapytania razem z ich pewnoÅ›ciÄ… ('certainity') w formie DataFrame

#todo: 2.e stwÃ³rz sÅ‚ownik synonimÃ³w i antonimÃ³w przy uÅ¼yciu streamlit i weaviate
# layout 2 kolumnowy
# 2 wejÅ›cia definiujÄ…ce sÅ‚owa "przyciÄ…gajÄ…ce" i "odpychajÄ…ce" (oddzielane przecinkiem lub Å›rednikiem)
# slider definujÄ…cy minimalnÄ… i maksymalnÄ… dÅ‚ugoÅ›Ä‡ sÅ‚Ã³w
# 2 wyjÅ›cia (tabele) - jedno z synonimami drugie z antonimami (do 30)



st.write('Awesome!')
st.balloons()