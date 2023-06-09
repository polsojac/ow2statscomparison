import requests
import base64
import os
from io import BytesIO
from flask import Flask,render_template, request, flash, redirect, url_for
from matplotlib.figure import Figure
from matplotlib import rcParams
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')
 
@app.route('/home')
def home():
    return render_template('home.html')
 
@app.route('/data/', methods = ['POST', 'GET'])
def data():
    if request.method == 'GET':
        return f"The URL /data is accessed directly. Try going to '/home' to submit form"
    if request.method == 'POST':
        form_data = request.form
        try:
            username_one = form_data['username-1']
        except:
            username_one = ''
        try:
            username_two = form_data['username-2']
        except:
            username_two = ''

        tank_heroes = ['dva', 'doomfist', 'junker-queen', 'orisa', 'ramattra', 'reinhardt', 'roadhog', 
                'sigma', 'winston', 'wrecking-ball', 'zarya']
        dmg_heroes = ['ashe', 'bastion', 'cassidy', 'echo', 'genji', 'hanzo', 'junkrat', 'mei', 'pharah', 
                'reaper', 'sojourn', 'soldier-76', 'sombra', 'symmetra', 'torbjorn', 'tracer', 'widowmaker']
        supp_heroes = ['ana', 'baptiste', 'brigitte', 'kiriko', 'lifeweaver', 'lucio', 'mercy', 'moira', 'zenyatta']

        username_one = username_one.replace('#', '-')
        username_two = username_two.replace('#', '-')
        qp_or_comp = form_data['qp-comp']
        hero = form_data['hero']
        params = {'gamemode': qp_or_comp, 'hero': hero}
        career_stats_one = requests.get(url='https://overfast-api.tekrop.fr/players/' + username_one + '/stats/career', 
        params=params)
        career_stats_two = requests.get(url='https://overfast-api.tekrop.fr/players/' + username_two + '/stats/career',
        params=params)
        if career_stats_one.status_code != 200 or career_stats_two.status_code != 200:
            flash('Must enter valid battle.net account (input is case-sensitive)')
            return redirect(url_for('home'))
        else:
            career_data_one = career_stats_one.json()
            career_data_two = career_stats_two.json()
            if career_data_one == {}:
                flash('First account is set to private or they have not played this hero in this gamemode')
                return redirect(url_for('home'))
            if career_data_two == {}:
                flash('Second account is set to private or they have not played this hero in this gamemode')
                return redirect(url_for('home'))
            else:
                try:
                    averages = career_data_one[hero]['average']
                except:
                    flash("Not enough data on this hero for first account")
                    return redirect(url_for('home'))
                try:
                    averages_two = career_data_two[hero]['average']
                except:
                    flash("Not enough data on this hero for second account")
                    return redirect(url_for('home'))
                rcParams.update({'figure.autolayout': True})
                if hero in tank_heroes:
                    tank_data = {}
                    tank_data_two = {}
                    
                    tank_data['Deaths Per 10'] = averages['deaths_avg_per_10_min']
                    tank_data['Elims Per 10'] = averages['eliminations_avg_per_10_min']
                    tank_data['Hero Dmg Per 10 (thousands)'] = averages['hero_damage_done_avg_per_10_min'] / 1000.0
                    tank_data['Obj Kills Per 10'] = averages['objective_kills_avg_per_10_min']
                    tank_data_two['Deaths Per 10'] = averages_two['deaths_avg_per_10_min']
                    tank_data_two['Elims Per 10'] = averages_two['eliminations_avg_per_10_min'] 
                    tank_data_two['Hero Dmg Per 10 (thousands)'] = averages_two['hero_damage_done_avg_per_10_min'] / 1000.0
                    tank_data_two['Obj Kills Per 10'] = averages_two['objective_kills_avg_per_10_min']
                    fig = Figure()
                    ax = fig.subplots()
                    bars = ax.barh(list(tank_data.keys()), list(tank_data.values()))
                    ax.bar_label(bars)
                    ax.invert_xaxis()
                    ax.yaxis.tick_right()
                    ax.yaxis.set_label_position("right")
                    # Save it to a temporary buffer.
                    buf = BytesIO()
                    fig.savefig(buf, format="png")
                    # Embed the result in the html output.
                    data = base64.b64encode(buf.getbuffer()).decode("ascii")
                    fig2 = Figure()
                    ax2 = fig2.subplots()
                    bars2 = ax2.barh(list(tank_data_two.keys()), list(tank_data_two.values()))
                    ax2.bar_label(bars2)
                    # Save it to a temporary buffer.
                    buf2 = BytesIO()
                    fig2.savefig(buf2, format="png")
                    # Embed the result in the html output.
                    data2 = base64.b64encode(buf2.getbuffer()).decode("ascii")
                    return render_template('data.html',averages=averages, data=data, hero=hero, data2=data2, username_one=username_one, username_two=username_two, qp_or_comp=qp_or_comp)
                elif hero in dmg_heroes:
                    dmg_data = {}
                    dmg_data_two = {}
                    dmg_data['Deaths Per 10'] = averages['deaths_avg_per_10_min']
                    dmg_data['Elims Per 10'] = averages['eliminations_avg_per_10_min']
                    dmg_data['Hero Dmg Per 10 (thousands)'] = averages['hero_damage_done_avg_per_10_min'] / 1000.0
                    dmg_data['Final Blows Per 10'] = averages['final_blows_avg_per_10_min']
                    dmg_data_two['Deaths Per 10'] = averages_two['deaths_avg_per_10_min']
                    dmg_data_two['Elims Per 10'] = averages_two['eliminations_avg_per_10_min'] 
                    dmg_data_two['Hero Dmg Per 10 (thousands)'] = averages_two['hero_damage_done_avg_per_10_min'] / 1000.0
                    dmg_data_two['Final Blows Per 10'] = averages_two['final_blows_avg_per_10_min']
                    fig = Figure()
                    ax = fig.subplots()
                    bars = ax.barh(list(dmg_data.keys()), list(dmg_data.values()))
                    ax.bar_label(bars)
                    # Save it to a temporary buffer.
                    ax.invert_xaxis()
                    ax.yaxis.tick_right()
                    ax.yaxis.set_label_position("right")
                    buf = BytesIO()
                    fig.savefig(buf, format="png")
                    # Embed the result in the html output.
                    data = base64.b64encode(buf.getbuffer()).decode("ascii")
                    fig2 = Figure()
                    ax2 = fig2.subplots()
                    bars2 = ax2.barh(list(dmg_data_two.keys()), list(dmg_data_two.values()))
                    ax2.bar_label(bars2)
                    # Save it to a temporary buffer.
                    buf2 = BytesIO()
                    fig2.savefig(buf2, format="png")
                    # Embed the result in the html output.
                    data2 = base64.b64encode(buf2.getbuffer()).decode("ascii")
                    return render_template('data.html',averages=averages, data=data, hero=hero, data2=data2, username_one=username_one, username_two=username_two, qp_or_comp=qp_or_comp)
                elif hero in supp_heroes:
                    supp_data = {}
                    supp_data_two = {}
                    supp_data['Deaths Per 10'] = averages['deaths_avg_per_10_min']
                    supp_data['Elims Per 10'] = averages['eliminations_avg_per_10_min']
                    supp_data['Hero Dmg Per 10 (thousands)'] = averages['hero_damage_done_avg_per_10_min'] / 1000.0
                    supp_data['Healing Per 10 (thousands)'] = averages['healing_done_avg_per_10_min'] / 1000.0
                    supp_data_two['Deaths Per 10'] = averages_two['deaths_avg_per_10_min']
                    supp_data_two['Elims Per 10'] = averages_two['eliminations_avg_per_10_min']
                    supp_data_two['Hero Dmg Per 10 (thousands)'] = averages_two['hero_damage_done_avg_per_10_min'] / 1000.0
                    supp_data_two['Healing Per 10 (thousands)'] = averages_two['healing_done_avg_per_10_min'] / 1000.0
                    fig = Figure()
                    ax = fig.subplots()
                    bars = ax.barh(list(supp_data.keys()), list(supp_data.values()))
                    ax.bar_label(bars)
                    ax.invert_xaxis()
                    ax.yaxis.tick_right()
                    ax.yaxis.set_label_position("right")
                    # Save it to a temporary buffer.
                    buf = BytesIO()
                    fig.savefig(buf, format="png")
                    # Embed the result in the html output.
                    data = base64.b64encode(buf.getbuffer()).decode("ascii")
                    fig2 = Figure()
                    ax2 = fig2.subplots()
                    bars2 = ax2.barh(list(supp_data_two.keys()), list(supp_data_two.values()))
                    ax2.bar_label(bars2)
                    # Save it to a temporary buffer.
                    buf2 = BytesIO()
                    fig2.savefig(buf2, format="png")
                    # Embed the result in the html output.
                    data2 = base64.b64encode(buf2.getbuffer()).decode("ascii")
                    return render_template('data.html',averages=averages, data=data, hero=hero, data2=data2, username_one=username_one, username_two=username_two, qp_or_comp=qp_or_comp)
        
 
 
app.run(host='localhost', port=5000)