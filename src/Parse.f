c----------------------------------------------------------------
c
c Converts protein primary sequence to 3-letter alphabet where
c F (folded), D (disordered), P (phase separating) predicts
c domain-level structure. Calculates from sequence a model
c of the polymer scaling exponent, nu, and the beta turn
c propensity for 25-residue windows.
c
c STW 07/02/2020
c
c----------------------------------------------------------------

      program Parse
      implicit none

      integer length,num,i,j,npep,jj,
     &        window_size,jjj,middle_position,
     &        num_ala,num_cys,num_asp,num_glu,num_phe,
     &        num_gly,num_his,num_ile,num_lys,num_leu,
     &        num_met,num_asn,num_pro,num_gln,num_arg,
     &        num_ser,num_thr,num_val,num_trp,num_tyr,
     &        num_ala_w,num_cys_w,num_asp_w,num_glu_w,num_phe_w,
     &        num_gly_w,num_his_w,num_ile_w,num_lys_w,num_leu_w,
     &        num_met_w,num_asn_w,num_pro_w,num_gln_w,num_arg_w,
     &        num_ser_w,num_thr_w,num_val_w,num_trp_w,num_tyr_w,
     &        count_regions,count_p,count_w,region,
     &        p_region_start,p_region_end,p_start(10000),
     &        p_end(10000),count_regions_p,count_regions_d,
     &        count_regions_f,d_start(10000),d_end(10000),
     &        f_start(10000),f_end(10000),count_domains,low,
     &        domain(10000)
      character code_inp*11000,code(11000)*3,classification(11000)*3
      real pppiia_h,pppiip_h,pppiig_h,pppiic_h,pppiid_h,pppiie_h,
     &     pppiif_h,pppiih_h,pppiii_h,pppiik_h,pppiil_h,pppiim_h,
     &     pppiin_h,pppiiq_h,pppiir_h,pppiis_h,pppiit_h,pppiiv_h,
     &     pppiiw_h,pppiiy_h,slope,intercept,v_line,net_charge_w,
     &     sum_ppii,v_exponent,fppii,turn,v_flory,rh_w,
     &     beta_a,beta_c,beta_d,beta_e,beta_f,beta_g,beta_h,beta_i,
     &     beta_k,beta_l,beta_m,beta_n,beta_p,beta_q,beta_r,beta_s,
     &     beta_t,beta_v,beta_w,beta_y,percent_p,percent_cutoff,
     &     r_model(10000),whole_seq_turn,whole_seq_nu,
     &     whole_seq_r_model,rh,net_charge


c PPII bias measured in peptides by Hilser group, used to calculate Rh.
c Prot Sci 2013, vol 22, pgs 405-417, in a table in supplementary information

      pppiia_h=0.37
      pppiic_h=0.25
      pppiid_h=0.30
      pppiie_h=0.42
      pppiif_h=0.17
      pppiig_h=0.13
      pppiih_h=0.20
      pppiii_h=0.39
      pppiik_h=0.56
      pppiil_h=0.24
      pppiim_h=0.36
      pppiin_h=0.27
      pppiip_h=1.00
      pppiiq_h=0.53
      pppiir_h=0.38
      pppiis_h=0.24
      pppiit_h=0.32
      pppiiv_h=0.39
      pppiiw_h=0.25
      pppiiy_h=0.25

c normalized frequency for beta-turn from Levitt (Biochemistry 1978, vol 17, pgs 4277-4285).

      beta_a=0.770
      beta_c=0.810
      beta_d=1.410
      beta_e=0.990
      beta_f=0.590
      beta_g=1.640
      beta_h=0.680
      beta_i=0.510
      beta_k=0.960
      beta_l=0.580
      beta_m=0.410
      beta_n=1.280
      beta_p=1.910
      beta_q=0.980
      beta_r=0.880
      beta_s=1.320
      beta_t=1.040
      beta_v=0.470
      beta_w=0.760
      beta_y=1.050


c Read input protein sequence.

      call get_command_argument(1,code_inp)
      if (len_trim(code_inp) == 0) then
      write(*,*)'no input argument, exiting program'
      stop
      endif

      length=len(code_inp)

c  convert any lower case letter to upper case.
    
      do i=1,length
         num=ichar(code_inp(i:i))
         if (num.ge.97.and.num.le.122) code_inp(i:i) = char(num-32)
      enddo

c  Determine sequence length.

      j=0
      do i=1,length
      if (code_inp(i:i).eq.' ') goto 1
         j=j+1
         code(j)=code_inp(i:i)
1     continue
      enddo 
      npep=j

c Define window size.

      window_size=25

c if protein sequence is less than the window size, stop

      if (npep.lt.window_size) then
      write(*,*)' '
      write(*,*)'input sequence is too short'
      write(*,*)'minimum sequence length is ',window_size
      write(*,*)' '
      stop
      endif

c if protein sequence is too long, stop

      if (npep.gt.10000) then
      write(*,*)' '
      write(*,*)'input sequence is too long'
      write(*,*)'maximum sequence length is 10000'
      write(*,*)' '
      stop
      endif

c calculate nu and turn propensity for the whole sequence

      num_ala=0
      num_cys=0
      num_asp=0
      num_glu=0
      num_phe=0
      num_gly=0
      num_his=0
      num_ile=0
      num_lys=0
      num_leu=0
      num_met=0
      num_asn=0
      num_pro=0
      num_gln=0
      num_arg=0
      num_ser=0
      num_thr=0
      num_val=0
      num_trp=0
      num_tyr=0

      DO J=1,NPEP
         IF (CODE(J).EQ.'A') THEN
            num_ala=num_ala+1
         endif
         IF (CODE(J).EQ.'C') THEN
            num_cys=num_cys+1
         endif
         IF (CODE(J).EQ.'D') THEN
            num_asp=num_asp+1
         endif
         IF (CODE(J).EQ.'E') THEN
            num_glu=num_glu+1
         endif
         IF (CODE(J).EQ.'F') THEN
            num_phe=num_phe+1
         endif
         IF (CODE(J).EQ.'G') THEN
            num_gly=num_gly+1
         endif
         IF (CODE(J).EQ.'H') THEN
            num_his=num_his+1
         endif
         IF (CODE(J).EQ.'I') THEN
            num_ile=num_ile+1
         endif
         IF (CODE(J).EQ.'K') THEN
            num_lys=num_lys+1
         endif
         IF (CODE(J).EQ.'L') THEN
            num_leu=num_leu+1
         endif
         IF (CODE(J).EQ.'M') THEN
            num_met=num_met+1
         endif
         IF (CODE(J).EQ.'N') THEN
            num_asn=num_asn+1
         endif
         IF (CODE(J).EQ.'P') THEN
            num_pro=num_pro+1
         endif
         IF (CODE(J).EQ.'Q') THEN
            num_gln=num_gln+1
         endif
         IF (CODE(J).EQ.'R') THEN
            num_arg=num_arg+1
         endif
         IF (CODE(J).EQ.'S') THEN
            num_ser=num_ser+1
         endif
         IF (CODE(J).EQ.'T') THEN
            num_thr=num_thr+1
         endif
         IF (CODE(J).EQ.'V') THEN
            num_val=num_val+1
         endif
         IF (CODE(J).EQ.'W') THEN
            num_trp=num_trp+1
         endif
         IF (CODE(J).EQ.'Y') THEN
            num_tyr=num_tyr+1
         endif
      enddo

      net_charge=abs(num_asp+num_glu
     &                  -num_lys-num_arg)

      sum_ppii=0.0

      sum_ppii=num_ala*pppiia_h+num_cys*pppiic_h
     &        +num_asp*pppiid_h+num_glu*pppiie_h
     &        +num_phe*pppiif_h+num_gly*pppiig_h
     &        +num_his*pppiih_h+num_ile*pppiii_h
     &        +num_lys*pppiik_h+num_leu*pppiil_h
     &        +num_met*pppiim_h+num_asn*pppiin_h
     &        +num_pro*pppiip_h+num_gln*pppiiq_h
     &        +num_arg*pppiir_h+num_ser*pppiis_h
     &        +num_thr*pppiit_h+num_val*pppiiv_h
     &        +num_trp*pppiiw_h+num_tyr*pppiiy_h

      fppii=sum_ppii/real(npep)
      v_exponent=0.503-0.11*log(1.0-fppii)

      rh=2.16*(real(npep)**(v_exponent))
     &    +0.26*real(net_charge)
     &    -0.29*(real(npep)**(0.5))
      v_flory=log(rh/2.16)/log(real(npep))

      turn=0.0

      turn=num_ala*beta_a+num_cys*beta_c
     &        +num_asp*beta_d+num_glu*beta_e
     &        +num_phe*beta_f+num_gly*beta_g
     &        +num_his*beta_h+num_ile*beta_i
     &        +num_lys*beta_k+num_leu*beta_l
     &        +num_met*beta_m+num_asn*beta_n
     &        +num_pro*beta_p+num_gln*beta_q
     &        +num_arg*beta_r+num_ser*beta_s
     &        +num_thr*beta_t+num_val*beta_v
     &        +num_trp*beta_w+num_tyr*beta_y
      turn=turn/real(npep)

      whole_seq_turn=turn
      whole_seq_nu=v_flory
      whole_seq_r_model=turn/v_flory


c calculate nu and turn propensity for each window

      DO J=1,NPEP
         if (j.le.(NPEP-window_size+1)) then
         middle_position=j+window_size/2

      num_ala_w=0
      num_cys_w=0
      num_asp_w=0
      num_glu_w=0
      num_phe_w=0
      num_gly_w=0
      num_his_w=0
      num_ile_w=0
      num_lys_w=0
      num_leu_w=0
      num_met_w=0
      num_asn_w=0
      num_pro_w=0
      num_gln_w=0
      num_arg_w=0
      num_ser_w=0
      num_thr_w=0
      num_val_w=0
      num_trp_w=0
      num_tyr_w=0

      DO JJJ=J,J+window_size-1
         IF (CODE(JJJ).EQ.'A') THEN
            num_ala_w=num_ala_w+1
         endif
         IF (CODE(JJJ).EQ.'C') THEN
            num_cys_w=num_cys_w+1
         endif
         IF (CODE(JJJ).EQ.'D') THEN
            num_asp_w=num_asp_w+1
         endif
         IF (CODE(JJJ).EQ.'E') THEN
            num_glu_w=num_glu_w+1
         endif
         IF (CODE(JJJ).EQ.'F') THEN
            num_phe_w=num_phe_w+1
         endif
         IF (CODE(JJJ).EQ.'G') THEN
            num_gly_w=num_gly_w+1
         endif
         IF (CODE(JJJ).EQ.'H') THEN
            num_his_w=num_his_w+1
         endif
         IF (CODE(JJJ).EQ.'I') THEN
            num_ile_w=num_ile_w+1
         endif
         IF (CODE(JJJ).EQ.'K') THEN
            num_lys_w=num_lys_w+1
         endif
         IF (CODE(JJJ).EQ.'L') THEN
            num_leu_w=num_leu_w+1
         endif
         IF (CODE(JJJ).EQ.'M') THEN
            num_met_w=num_met_w+1
         endif
         IF (CODE(JJJ).EQ.'N') THEN
            num_asn_w=num_asn_w+1
         endif
         IF (CODE(JJJ).EQ.'P') THEN
            num_pro_w=num_pro_w+1
         endif
         IF (CODE(JJJ).EQ.'Q') THEN
            num_gln_w=num_gln_w+1
         endif
         IF (CODE(JJJ).EQ.'R') THEN
            num_arg_w=num_arg_w+1
         endif
         IF (CODE(JJJ).EQ.'S') THEN
            num_ser_w=num_ser_w+1
         endif
         IF (CODE(JJJ).EQ.'T') THEN
            num_thr_w=num_thr_w+1
         endif
         IF (CODE(JJJ).EQ.'V') THEN
            num_val_w=num_val_w+1
         endif
         IF (CODE(JJJ).EQ.'W') THEN
            num_trp_w=num_trp_w+1
         endif
         IF (CODE(JJJ).EQ.'Y') THEN
            num_tyr_w=num_tyr_w+1
         endif
      enddo

      net_charge_w=abs(num_asp_w+num_glu_w
     &                  -num_lys_w-num_arg_w)

      sum_ppii=0.0

      sum_ppii=num_ala_w*pppiia_h+num_cys_w*pppiic_h
     &        +num_asp_w*pppiid_h+num_glu_w*pppiie_h
     &        +num_phe_w*pppiif_h+num_gly_w*pppiig_h
     &        +num_his_w*pppiih_h+num_ile_w*pppiii_h
     &        +num_lys_w*pppiik_h+num_leu_w*pppiil_h
     &        +num_met_w*pppiim_h+num_asn_w*pppiin_h
     &        +num_pro_w*pppiip_h+num_gln_w*pppiiq_h
     &        +num_arg_w*pppiir_h+num_ser_w*pppiis_h
     &        +num_thr_w*pppiit_h+num_val_w*pppiiv_h
     &        +num_trp_w*pppiiw_h+num_tyr_w*pppiiy_h

      fppii=sum_ppii/real(window_size)
      v_exponent=0.503-0.11*log(1.0-fppii)

c multiplier of 4 on the sequence, to put nu into the length-independent range

      rh_w=2.16*(real(4*window_size)**(v_exponent))
     &    +0.26*real(4*net_charge_w)
     &    -0.29*(real(4*window_size)**(0.5))
      v_flory=log(rh_w/2.16)/log(real(4*window_size))

      turn=0.0

      turn=num_ala_w*beta_a+num_cys_w*beta_c
     &        +num_asp_w*beta_d+num_glu_w*beta_e
     &        +num_phe_w*beta_f+num_gly_w*beta_g
     &        +num_his_w*beta_h+num_ile_w*beta_i
     &        +num_lys_w*beta_k+num_leu_w*beta_l
     &        +num_met_w*beta_m+num_asn_w*beta_n
     &        +num_pro_w*beta_p+num_gln_w*beta_q
     &        +num_arg_w*beta_r+num_ser_w*beta_s
     &        +num_thr_w*beta_t+num_val_w*beta_v
     &        +num_trp_w*beta_w+num_tyr_w*beta_y
      turn=turn/real(window_size)


c for the null IDP set (using predicted Rh and Levitt turn propensity) the averages are
c v_flory = 0.557 +- 0.020 and turn = 1.062 +- 0.082
c Used to define the PS, ID, and Folded sectors of a turn vs nu plot


      r_model(middle_position)=turn/v_flory
      if(v_flory.ge.(0.557)) then
         classification(middle_position)='D'
         goto 10
      endif
      if(turn.gt.(1.144).and.v_flory.lt.(0.557)) then
         classification(middle_position)='P'
         goto 10
      endif
      if(turn.gt.(1.062).and.v_flory.lt.(0.537)) then
         classification(middle_position)='P'
         goto 10
      endif

      slope=0.020/0.082
      intercept=0.537-slope*1.062
      v_line=slope*turn+intercept

      if(turn.gt.(1.062).and.v_flory.lt.v_line) then
         classification(middle_position)='P'
         goto 10
      endif
      if(turn.gt.(1.062).and.v_flory.ge.v_line) then
         classification(middle_position)='D'
         goto 10
      endif
      if(turn.le.(0.98).and.v_flory.lt.(0.557)) then
         classification(middle_position)='F'
         goto 10
      endif
      if(turn.le.(1.062).and.v_flory.lt.(0.537)) then
         classification(middle_position)='F'
         goto 10
      endif

      slope=-0.020/0.082
      intercept=0.537-slope*1.062
      v_line=slope*turn+intercept

      if(turn.le.(1.062).and.v_flory.lt.v_line) then
         classification(middle_position)='F'
         goto 10
      endif
      if(turn.le.(1.062).and.v_flory.ge.v_line) then
         classification(middle_position)='D'
         goto 10
      endif

10    continue
      endif
      enddo

      do j=1,window_size/2
         classification(j)=classification((window_size/2)+1)
         r_model(j)=r_model((window_size/2)+1)
      enddo
      do j=npep-(window_size/2)+1,npep
         classification(j)=classification(npep-(window_size/2))
         r_model(j)=r_model(npep-(window_size/2))
      enddo


      write(*,*)' '
      write(*,'(11000a1)')(classification(j),j=1,npep)

      write(*,*)' '
      write(*,'("Sequence length ",i6)')npep
      write(*,'("Whole sequence nu_model ",f6.3)')whole_seq_nu
      write(*,'("Whole sequence β-turn prop ",f6.3)')whole_seq_turn
      write(*,'("Whole sequence r_model  ",f6.3)')whole_seq_r_model

      open (7,file='residue_level_rmodel.csv')
      do j=1,npep
      write(7,'(i6,", ",a1,", ",a1,",",f6.3)')j,code(j),
     & classification(j),r_model(j)
      enddo
      close(7)

      percent_cutoff=0.90
c find PS (blue) regions 20 residues or longer and labeled P at the percent_cutoff or higher
      i=1
      count_regions=0
20    continue
      count_p=0
      count_w=0
      do j=i,i+19
      region=0
      count_w=count_w+1
      if(classification(j).eq.'P') count_p=count_p+1
      enddo
30    continue
      percent_p=real(count_p)/real(count_w)
      if(percent_p.ge.percent_cutoff) then
         region=1
         p_region_start=i
         p_region_end=j
         if(j.lt.npep) then
         j=j+1
         count_w=count_w+1
         if(classification(j).eq.'P') then
            count_p=count_p+1
         endif
         goto 30
         endif
      endif
      if(region.eq.1) then
         i=j
         count_regions=count_regions+1
         p_start(count_regions)=p_region_start
         p_end(count_regions)=p_region_end
      endif
      if(region.eq.0) i=i+1
      if((i+19).le.npep) goto 20
      count_regions_p=count_regions

c find ID (red) regions 20 residues or longer and labeled D at the percent_cutoff or higher
      i=1
      count_regions=0
40    continue
      count_p=0
      count_w=0
      do j=i,i+19
      region=0
      count_w=count_w+1
      if(classification(j).eq.'D') count_p=count_p+1
      enddo
50    continue
      percent_p=real(count_p)/real(count_w)
      if(percent_p.ge.percent_cutoff) then
         region=1
         p_region_start=i
         p_region_end=j
         if(j.lt.npep) then
         j=j+1
         count_w=count_w+1
         if(classification(j).eq.'D') then
            count_p=count_p+1
         endif
         goto 50
         endif
      endif
      if(region.eq.1) then
         i=j
         count_regions=count_regions+1
         d_start(count_regions)=p_region_start
         d_end(count_regions)=p_region_end
      endif
      if(region.eq.0) i=i+1
      if((i+19).le.npep) goto 40
      count_regions_d=count_regions

c find F (black) regions 20 residues or longer and labeled F at the percent_cutoff or higher
      i=1
      count_regions=0
60    continue
      count_p=0
      count_w=0
      do j=i,i+19
      region=0
      count_w=count_w+1
      if(classification(j).eq.'F') count_p=count_p+1
      enddo
70    continue
      percent_p=real(count_p)/real(count_w)
      if(percent_p.ge.percent_cutoff) then
         region=1
         p_region_start=i
         p_region_end=j
         if(j.lt.npep) then
         j=j+1
         count_w=count_w+1
         if(classification(j).eq.'F') then
            count_p=count_p+1
         endif
         goto 70
         endif
      endif
      if(region.eq.1) then
         i=j
         count_regions=count_regions+1
         f_start(count_regions)=p_region_start
         f_end(count_regions)=p_region_end
      endif
      if(region.eq.0) i=i+1
      if((i+19).le.npep) goto 60
      count_regions_f=count_regions

c find first domain (earliest in sequence) and identify its first residue
      count_domains=count_regions_p+count_regions_d+count_regions_f
      low=1000000
      j=1
      if(j.le.count_domains) then
      do i=1,count_regions_p
         if(p_start(i).lt.low) low=p_start(i)
      enddo
      do i=1,count_regions_d
         if(d_start(i).lt.low) low=d_start(i)
      enddo
      do i=1,count_regions_f
         if(f_start(i).lt.low) low=f_start(i)
      enddo
      domain(j)=low
      endif

c find first residue of each additional domain in successive order
80    j=j+1
      low=1000000
      if(j.le.count_domains) then
      do i=1,count_regions_p
         if(p_start(i).lt.low.and.p_start(i).gt.domain(j-1)) 
     &      low=p_start(i)
      enddo
      do i=1,count_regions_d
         if(d_start(i).lt.low.and.d_start(i).gt.domain(j-1)) 
     &      low=d_start(i)
      enddo
      do i=1,count_regions_f
         if(f_start(i).lt.low.and.f_start(i).gt.domain(j-1)) 
     &      low=f_start(i)
      enddo
      domain(j)=low
      goto 80
      endif

c correct for domain-domain overlap when present
      if(count_domains.gt.1) then
c find overlapping domains and split the overlap, which is percent_cutoff*20/2
      do i=1,count_domains-1
      do j=1,count_regions_p
         if(p_start(j).eq.domain(i)) then
         if(p_end(j).ge.domain(i+1)) then
            p_end(j)=domain(i+1)+int((1.0-percent_cutoff)*20.0/2.0)
            do jj=1,count_regions_d
            if(d_start(jj).eq.domain(i+1)) then
               d_start(jj)=p_end(j)+1
               domain(i+1)=d_start(jj)
            endif
            enddo
            do jj=1,count_regions_f
            if(f_start(jj).eq.domain(i+1)) then
               f_start(jj)=p_end(j)+1
               domain(i+1)=f_start(jj)
            endif
            enddo
         endif
         endif
      enddo
      do j=1,count_regions_d
         if(d_start(j).eq.domain(i)) then
         if(d_end(j).ge.domain(i+1)) then
            d_end(j)=domain(i+1)+int((1.0-percent_cutoff)*20.0/2.0)
            do jj=1,count_regions_p
            if(p_start(jj).eq.domain(i+1)) then
               p_start(jj)=d_end(j)+1
               domain(i+1)=p_start(jj)
            endif
            enddo
            do jj=1,count_regions_f
            if(f_start(jj).eq.domain(i+1)) then
               f_start(jj)=d_end(j)+1
               domain(i+1)=f_start(jj)
            endif
            enddo
         endif
         endif
      enddo
      do j=1,count_regions_f
         if(f_start(j).eq.domain(i)) then
         if(f_end(j).ge.domain(i+1)) then
            f_end(j)=domain(i+1)+int((1.0-percent_cutoff)*20.0/2.0)
            do jj=1,count_regions_d
            if(d_start(jj).eq.domain(i+1)) then
               d_start(jj)=f_end(j)+1
               domain(i+1)=d_start(jj)
            endif
            enddo
            do jj=1,count_regions_p
            if(p_start(jj).eq.domain(i+1)) then
               p_start(jj)=f_end(j)+1
               domain(i+1)=p_start(jj)
            endif
            enddo
         endif
         endif
      enddo
      enddo
      endif

      write(*,*)' '
      write(*,'("Number of PS (blue) domains = ",i6)')count_regions_p
      write(*,'("domain  first_residue  last_residue")')
      do i=1,count_regions_p
      write(*,'(i4,7x,i6,7x,i6)') i,p_start(i),p_end(i)
      enddo
      write(*,*)' '
      write(*,'("Number of ID (red) domains = ",i7)')count_regions_d
      write(*,'("domain  first_residue  last_residue")')
      do i=1,count_regions_d
      write(*,'(i4,7x,i6,7x,i6)') i,d_start(i),d_end(i)
      enddo
      write(*,*)' '
      write(*,'("Number of F (black) domains = ",i5)')count_regions_f
      write(*,'("domain  first_residue  last_residue")')
      do i=1,count_regions_f
      write(*,'(i4,7x,i6,7x,i6)') i,f_start(i),f_end(i)
      enddo

      write(*,*)' '
      do i=1,count_domains
      do j=1,count_regions_p
         if(p_start(j).eq.domain(i)) then
         write(*,'("domain ",i4,", PS (blue)",",  first residue ",i5,
     &    ",  last residue ",i5,",  length ",i6)')i,p_start(j),
     &    p_end(j),(p_end(j)-p_start(j)+1)
         endif
      enddo
      do j=1,count_regions_d
         if(d_start(j).eq.domain(i)) then
         write(*,'("domain ",i4,", ID  (red)",",  first residue ",i5,
     &    ",  last residue ",i5,",  length ",i6)')i,d_start(j),
     &    d_end(j),(d_end(j)-d_start(j)+1)
         endif
      enddo
      do j=1,count_regions_f
         if(f_start(j).eq.domain(i)) then
         write(*,'("domain ",i4,", F (black)",",  first residue ",i5,
     &    ",  last residue ",i5,",  length ",i6)')i,f_start(j),
     &    f_end(j),(f_end(j)-f_start(j)+1)
         endif
      enddo
      enddo

      end